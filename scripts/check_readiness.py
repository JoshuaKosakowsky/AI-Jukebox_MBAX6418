"""Repository coverage and frozen-candidate release checks; never calls services."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_IDS = {f'R{i:02}' for i in range(1, 37)}
MODES = {'review', 'live', 'browser', 'asset-review', 'zip-install'}
PLACEHOLDERS = {'', 'pending', 'tbd', 'not run', 'not tested', 'unchecked'}


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)


def read_registry(root):
    return json.loads((root / 'docs/acceptance.json').read_text(encoding='utf-8'))


def coverage_errors(registry, root):
    errors = []
    rows = registry.get('requirements', [])
    ids = [r.get('id') for r in rows]
    if set(ids) != REQUIRED_IDS or len(ids) != len(set(ids)):
        errors.append('Required R01-R36 coverage changed, missing or duplicated; audit the brief')
    tasks = registry.get('tasks', {})
    cases = registry.get('cases', {})
    if not tasks or not cases:
        errors.append('Task and acceptance-case definitions are required')
    used_tasks, used_cases = set(), set()
    for row in rows:
        name = row.get('id', '?')
        if not row.get('statement') or not row.get('source'):
            errors.append(f'{name}: missing requirement or source')
        task = row.get('task')
        if task not in tasks:
            errors.append(f'{name}: unknown task {task}')
        used_tasks.add(task)
        if not row.get('cases'):
            errors.append(f'{name}: no acceptance cases')
        for case in row.get('cases', []):
            if case not in cases:
                errors.append(f'{name}: unknown case {case}')
            used_cases.add(case)
    if set(tasks) - used_tasks or set(cases) - used_cases:
        errors.append('Unmapped task or case; remove drift or connect it to requirements')
    for task, info in tasks.items():
        if not info.get('title') or not info.get('issue_anchor'):
            errors.append(f'{task}: missing issue title/anchor')
        for dependency in info.get('depends_on', []):
            if dependency not in tasks or dependency == task:
                errors.append(f'{task}: invalid dependency {dependency}')
        issue_file = root / 'docs/ISSUES.md'
        if issue_file.exists() and f'## {task} ' not in issue_file.read_text(encoding='utf-8'):
            errors.append(f'{task}: no concrete local issue brief')
    def cyclic(task, active):
        if task in active:
            return True
        return any(cyclic(dep, active | {task}) for dep in tasks.get(task, {}).get('depends_on', []) if dep in tasks)
    if any(cyclic(task, set()) for task in tasks):
        errors.append('Task dependencies contain a cycle')
    def depends_on(task, target, seen=None):
        seen = set() if seen is None else seen
        if task in seen:
            return False
        dependencies = tasks.get(task, {}).get('depends_on', [])
        return target in dependencies or any(depends_on(dep, target, seen | {task}) for dep in dependencies)
    for row in rows:
        for case in row.get('cases', []):
            owner = cases.get(case, {}).get('owner_task')
            if owner and owner != row.get('task') and depends_on(owner, row.get('task')):
                errors.append(f'{row.get("id")}: closure depends on a downstream task; split the acceptance scope')
    for case, info in cases.items():
        if info.get('owner_task') not in tasks:
            errors.append(f'{case}: missing acceptance owner task')
        modes = info.get('modes', [])
        if not info.get('expected') or not modes or not set(modes) <= MODES:
            errors.append(f'{case}: missing acceptance behavior or invalid modes')
    return errors


def evidence_template(registry):
    return {
        'tested_commit': None, 'prepared_by': None, 'installed_by': None,
        'environment': None, 'launch_command': None, 'repository_url': None, 'archive_url': None,
        'archive_sha256': None, 'public_access_checked_at': None,
        'team': [],
        'checks': {
            case: {'status': 'not-run', 'tester': None, 'inputs': None,
                   'expected': info['expected'], 'actual': None,
                   'modes': [], 'variants_tested': [], 'evidence': []}
            for case, info in registry['cases'].items()
        },
    }


def meaningful(value):
    return isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS


def safe_path(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '\\' not in name and ':' not in name and '..' not in p.parts


def forbidden(name):
    p = PurePosixPath(name)
    base = p.name.lower()
    private = {'uploads', 'user_uploads', 'voice_references', 'recordings', 'data', 'data_raw'}
    return (base == '.env' or (base.startswith('.env.') and base != '.env.example')
            or base == 'class-endpoints.txt' or bool(private.intersection(x.lower() for x in p.parts))
            or p.suffix.lower() in {'.key', '.pem'})


def archive_errors(archive_path, tracked, blob_reader):
    """Inspect ZIP without extracting; every submitted file must match the candidate."""
    errors = []
    try:
        with ZipFile(archive_path) as z:
            entries = [item for item in z.infolist() if not item.is_dir()]
            names = [item.filename for item in entries]
            if len(names) != len(set(names)):
                errors.append('ZIP has duplicate entries')
            if any(not safe_path(name) for name in names):
                return ['ZIP contains unsafe paths']
            # GitHub source archives have a single enclosing directory.
            prefixes = {name.split('/')[0] for name in names}
            prefix = next(iter(prefixes)) + '/' if len(prefixes) == 1 and all('/' in n for n in names) else ''
            files = {name[len(prefix):]: name for name in names}
            if set(files) != set(tracked):
                errors.append('ZIP file inventory differs from the candidate commit')
            for relative, member in files.items():
                if forbidden(relative):
                    errors.append(f'ZIP contains prohibited private file: {relative}')
                if relative in tracked:
                    with z.open(member) as stream:
                        digest = hashlib.file_digest(stream, 'sha256').digest()
                    if digest != hashlib.sha256(blob_reader(relative)).digest():
                        errors.append(f'ZIP content differs from candidate: {relative}')
    except (OSError, BadZipFile, RuntimeError) as exc:
        errors.append(f'ZIP could not be inspected ({type(exc).__name__})')
    return errors


def release_errors(registry, record, tracked, blob_reader):
    """Check completeness of recorded evidence; humans still validate its truth."""
    errors = []
    commit = record.get('tested_commit', '')
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        errors.append('Exact 40-character tested_commit is required')
    for name in ('prepared_by', 'installed_by', 'environment', 'launch_command', 'public_access_checked_at'):
        if not meaningful(record.get(name)):
            errors.append(f'Missing {name}')
    if record.get('prepared_by') == record.get('installed_by'):
        errors.append('Independent ZIP installer must differ from candidate preparer')
    repo = record.get('repository_url') or ''
    url = urlparse(repo)
    if url.scheme != 'https' or url.netloc != 'github.com' or not re.fullmatch(r'/[^/]+/[^/]+', url.path):
        errors.append('A public GitHub repository URL is required')
    expected_archive = repo.rstrip('/') + f'/archive/{commit}.zip'
    if record.get('archive_url') != expected_archive:
        errors.append('Record the GitHub source ZIP URL for exactly tested_commit')
    for case, info in registry['cases'].items():
        observed = record.get('checks', {}).get(case, {})
        if observed.get('status') != 'pass':
            errors.append(f'{case}: not verified (blocked/skipped/not-run are not passes)')
            continue
        for field in ('tester', 'inputs', 'expected', 'actual'):
            if not meaningful(observed.get(field)):
                errors.append(f'{case}: missing {field}')
        if not set(info['modes']) <= set(observed.get('modes', [])):
            errors.append(f'{case}: missing required verification modes {info["modes"]}')
        if not set(info.get('variants', [])) <= set(observed.get('variants_tested', [])):
            errors.append(f'{case}: not all required variants were exercised')
        evidence = observed.get('evidence', [])
        if not evidence or any(not safe_path(p) or p not in tracked for p in evidence):
            errors.append(f'{case}: evidence must reference files in the candidate')
    if record.get('checks', {}).get('AT-16', {}).get('tester') != record.get('installed_by'):
        errors.append('AT-16 must identify the actual independent ZIP installer as tester')
    team = record.get('team', [])
    members = [r.get('teammate') for r in team]
    if len(team) < 2 or len(set(members)) != len(members) or not all(meaningful(m) for m in members):
        errors.append('List the actual team (at least two distinct teammates)')
    for row in team:
        if not meaningful(row.get('contribution_evidence')) or not meaningful(row.get('review_evidence')):
            errors.append('Every teammate needs meaningful contribution and teammate-review evidence')
    if record.get('prepared_by') not in members or record.get('installed_by') not in members:
        errors.append('Candidate preparer and installer must be identified team members')
    try:
        samples = json.loads(blob_reader('assets/samples/manifest.json'))['samples']
        if len(samples) != 3 or len({s['id'] for s in samples}) != 3:
            errors.append('Three distinct approved sample tracks are required')
        if len({s.get('audio') for s in samples}) != 3 or len({s.get('cover') for s in samples}) != 3:
            errors.append('Samples need three distinct audio/cover paths')
        for sample in samples:
            for field in ('title', 'generated_at', 'generation_notes'):
                if not meaningful(sample.get(field)):
                    errors.append(f'Sample missing {field}')
            for field in ('audio', 'cover'):
                name = sample.get(field, '')
                if not safe_path(name) or not name.startswith('assets/samples/') or name not in tracked or not blob_reader(name):
                    errors.append(f'Sample has missing/invalid {field} asset')
            models = sample.get('generated_with', {})
            if models.get('music') != 'ACE-Step 1.5 XL Turbo' or models.get('cover') != 'FLUX.2 klein 4B':
                errors.append('Samples must record the required class music/cover services')
            if sample.get('instrumental') is not True and (models.get('lyrics') != 'Qwen3.6-35B-A3B' or not meaningful(sample.get('lyrics'))):
                errors.append('Vocal samples require AI-lyric text and class provenance')
    except (KeyError, ValueError, TypeError):
        errors.append('Sample manifest missing or malformed')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--template', type=Path, help='Write a blank record outside the frozen candidate')
    args = parser.parse_args()
    registry = read_registry(ROOT)
    errors = coverage_errors(registry, ROOT)
    if errors:
        print('\n'.join('FAIL: ' + e for e in errors))
        return 1
    if args.template:
        if args.template.exists():
            parser.error('Refusing to overwrite an existing evidence record')
        args.template.parent.mkdir(parents=True, exist_ok=True)
        args.template.write_text(json.dumps(evidence_template(registry), indent=2) + '\n', encoding='utf-8')
        print('Blank evidence template written; every acceptance case remains not-run.')
        return 0
    if not args.release:
        print(f'PASS: coverage structure only ({len(REQUIRED_IDS)} requirements, {len(registry["tasks"])} tasks, {len(registry["cases"])} cases).')
        print('Application/release readiness NOT evaluated. Run --release with actual evidence and the GitHub ZIP.')
        return 0
    if not args.evidence or not args.archive:
        print('NOT READY: provide --evidence <completed-record.json> and --archive <GitHub-source.zip>.')
        return 1
    try:
        record = json.loads(args.evidence.read_text(encoding='utf-8'))
        if not isinstance(record, dict):
            raise ValueError('Evidence must be an object')
        commit = record.get('tested_commit')
        if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise ValueError('Exact candidate SHA required')
        git(ROOT, 'cat-file', '-e', commit + '^{commit}')
        git(ROOT, 'merge-base', '--is-ancestor', commit, 'main')
        tracked = set(git(ROOT, 'ls-tree', '-r', '--name-only', commit).decode().splitlines())
        blob = lambda path: git(ROOT, 'show', f'{commit}:{path}')
        if json.loads(blob('docs/acceptance.json')) != registry:
            errors.append('Candidate has different requirement coverage; check it with its own gate')
        errors += release_errors(registry, record, tracked, blob)
        if record.get('archive_sha256') != hashlib.sha256(args.archive.read_bytes()).hexdigest():
            errors.append('Archive SHA-256 differs from the independently tested ZIP')
        errors += archive_errors(args.archive, tracked, blob)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError):
        errors.append('Cannot validate candidate/evidence/archive; candidate must exist on main and inputs must be valid')
    if errors:
        print('\n'.join('NOT READY: ' + e for e in errors))
        return 1
    print('PASS: recorded release gates and archive identity. Human review of evidence and actual functionality remains essential.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
