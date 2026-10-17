"""Offline scaffold and tracked-file checks; no app functionality is claimed."""
from pathlib import Path, PurePosixPath
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


required = [
    'AGENTS.md', 'CONTRIBUTING.md', 'PLAN.md', 'README.md', 'handoff.md',
    '.env.example', '.gitignore', '.gitattributes', '.github/workflows/ci.yml',
    '.github/main-protection.json', '.github/PULL_REQUEST_TEMPLATE.md',
    '.github/ISSUE_TEMPLATE/bug_report.md',
    '.github/ISSUE_TEMPLATE/feature_request.md',
    '.githooks/pre-commit', '.githooks/pre-push', 'docs/ASSIGNMENT.md',
    'docs/COMMITS.md', 'docs/TESTING.md', 'docs/TEST_RESULTS.md',
    'docs/GITHUB_SETUP.md', 'assets/samples/README.md', 'results/README.md',
    'scripts/verify_repo.py', 'scripts/check_readiness.py',
    'docs/CONTRIBUTIONS.md', 'docs/acceptance.json', 'docs/ISSUES.md',
    'docs/A2_LESSONS.md', 'assets/samples/manifest.json', 'tests/test_readiness.py',
]
for name in required:
    require((ROOT / name).is_file(), f'Missing required file: {name}')

tracked = subprocess.check_output(
    ['git', 'ls-files', '-z'], cwd=ROOT
).decode('utf-8').split('\0')
tracked = [name for name in tracked if name]
require(bool(tracked), 'No tracked/staged files; run git add before validation')
require(set(required).issubset(tracked), 'Required scaffold files must be tracked')

private_dirs = {
    'uploads', 'user_uploads', 'voice_references', 'recordings',
    'data', 'data_raw', 'generated', 'outputs', 'tmp', 'temp', 'logs',
}
audio_suffixes = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.webm', '.mp4'}
secret = re.compile(
    rb'(?:sk-[A-Za-z0-9_-]{16,}|gh[pous]_[A-Za-z0-9]{20,}'
    rb'|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'
)
for name in tracked:
    path = PurePosixPath(name)
    base = path.name.lower()
    require(not (base == '.env' or
                 (base.startswith('.env.') and base != '.env.example')),
            f'Private environment file tracked: {name}')
    require(base != 'class-endpoints.txt', f'Private service file tracked: {name}')
    require(not private_dirs.intersection(p.lower() for p in path.parts[:-1]),
            f'Private/runtime directory tracked: {name}')
    require(path.suffix.lower() not in {'.pem', '.key', '.zip'},
            f'Private key or archive tracked: {name}')
    if path.suffix.lower() in audio_suffixes:
        require(path.parent == PurePosixPath('assets/samples'),
                f'Media outside approved samples: {name}')
    local = ROOT / name
    require(local.is_file(), f'Tracked file missing from worktree: {name}')
    if not local.is_file():
        continue
    content = local.read_bytes()
    require(not secret.search(content), f'Possible credential pattern: {name}')
    if path.suffix.lower() == '.md':
        text = content.decode('utf-8')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            target = unquote(target.split('#', 1)[0].split('?', 1)[0])
            require((local.parent / target).exists(),
                    f'Broken local link in {name}: {target}')

policy_path = ROOT / '.github/main-protection.json'
if policy_path.exists():
    policy = json.loads(policy_path.read_text())
    require(policy['required_status_checks'] == {
        'strict': True, 'checks': [{'context': 'test', 'app_id': 15368}]},
        'Required strict test check differs from baseline')
    require(policy['required_pull_request_reviews'] == {
        'dismiss_stale_reviews': True, 'require_code_owner_reviews': False,
        'require_last_push_approval': True, 'required_approving_review_count': 1},
        'Review policy differs from baseline')
    for key in ('enforce_admins', 'required_conversation_resolution'):
        require(policy.get(key) is True, f'Protection must enable {key}')
    for key in ('allow_force_pushes', 'allow_deletions', 'required_linear_history',
                'block_creations', 'lock_branch', 'allow_fork_syncing'):
        require(policy.get(key) is False, f'Protection differs: {key}')
    require(policy.get('restrictions') is None, 'Unexpected push restrictions')

handoff = ROOT / 'handoff.md'
if handoff.exists():
    text = handoff.read_text(encoding='utf-8')
    for heading in ('Session', 'Constraints', 'Repository state',
                    'Work completed and decisions', 'Validation',
                    'Blockers and unchecked areas', 'Next steps', 'References'):
        require(f'## {heading}' in text, f'Handoff section missing: {heading}')

if errors:
    print('\n'.join(f'FAIL: {message}' for message in errors))
    sys.exit(1)
print(f'PASS: scaffold, links, tracked-file safeguards and policy ({len(tracked)} files)')
print('Scope: repository only; application and service functionality not tested.')
