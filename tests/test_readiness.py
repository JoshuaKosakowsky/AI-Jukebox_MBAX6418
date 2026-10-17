"""Offline regressions for coverage/readiness claims, not jukebox behavior."""
import contextlib
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('gate', ROOT / 'scripts/check_readiness.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ReadinessChecks(unittest.TestCase):
    def setUp(self):
        self.registry = gate.read_registry(ROOT)

    def fixture(self):
        record = gate.evidence_template(self.registry)
        record.update(tested_commit='a'*40, prepared_by='owner', installed_by='reviewer',
                      environment='Test fixture only, no app run', launch_command='synthetic gate fixture only',
                      repository_url='https://github.com/test/example',
                      archive_url='https://github.com/test/example/archive/'+'a'*40+'.zip',
                      public_access_checked_at='2026-10-17T12:00:00-06:00',
                      team=[{'teammate': name, 'contribution_evidence': 'fixture-commit',
                             'review_evidence': 'fixture-review'} for name in ('owner','reviewer')])
        for case, observed in record['checks'].items():
            observed.update(status='pass', tester='reviewer', inputs='Synthetic gate input',
                            actual='Synthetic gate result; this is not application evidence',
                            modes=self.registry['cases'][case]['modes'],
                            variants_tested=self.registry['cases'][case].get('variants', []),
                            evidence=['results/fixture.md'])
        samples = [dict(id=f's{i}', title=f'Track {i}', audio=f'assets/samples/{i}.wav',
                        cover=f'assets/samples/{i}.png', instrumental=True,
                        generated_at='fixture date', generation_notes='Synthetic metadata only',
                        generated_with={'music':'ACE-Step 1.5 XL Turbo','cover':'FLUX.2 klein 4B'})
                   for i in range(3)]
        blobs = {'assets/samples/manifest.json': json.dumps({'samples':samples}).encode(),
                 'results/fixture.md': b'Synthetic gate evidence'}
        for sample in samples:
            blobs[sample['audio']] = b'fixture audio bytes, not playable sample evidence'
            blobs[sample['cover']] = b'fixture cover bytes, not rendered app evidence'
        return record, blobs

    def test_all_brief_requirements_have_task_and_case(self):
        self.assertEqual(gate.coverage_errors(self.registry, ROOT), [])

    def test_dropped_requirement_fails(self):
        self.registry['requirements'].pop()
        self.assertTrue(gate.coverage_errors(self.registry, ROOT))

    def test_duplicate_and_unmapped_requirement_fail(self):
        self.registry['requirements'][0]['id'] = 'R02'
        self.registry['requirements'][0]['cases'] = ['nonexistent-case']
        errors = gate.coverage_errors(self.registry, ROOT)
        self.assertTrue(any('duplicated' in e for e in errors))
        self.assertTrue(any('unknown case' in e for e in errors))

    def test_circular_dependencies_fail(self):
        self.registry['tasks']['A3-01']['depends_on'] = ['A3-02']
        self.assertTrue(any('cycle' in e for e in gate.coverage_errors(self.registry, ROOT)))

    def test_task_closure_cannot_wait_on_its_dependent_task(self):
        requirement = next(row for row in self.registry['requirements'] if row['id']=='R08')
        requirement['cases'].append('AT-04')
        self.assertTrue(any('closure depends on a downstream task' in e for e in gate.coverage_errors(self.registry, ROOT)))

    def test_valid_metadata_does_not_claim_actual_app_testing(self):
        record, blobs = self.fixture()
        self.assertEqual(gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__), [])

    def test_skipped_case_is_not_a_pass(self):
        record, blobs = self.fixture()
        record['checks']['AT-03']['status'] = 'skipped'
        self.assertTrue(any('AT-03: not verified' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_stubbed_browser_result_cannot_replace_live_verification(self):
        record, blobs = self.fixture()
        record['checks']['AT-03']['modes'] = ['browser']
        self.assertTrue(any('AT-03: missing required verification' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_both_reference_formats_must_be_checked(self):
        record, blobs = self.fixture()
        record['checks']['AT-08']['variants_tested'] = ['mp3']
        self.assertTrue(any('AT-08: not all' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_empty_results_and_untracked_evidence_fail(self):
        record, blobs = self.fixture()
        record['checks']['AT-03']['actual'] = 'not run'
        record['checks']['AT-03']['evidence'] = ['missing.png']
        errors = gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)
        self.assertTrue(any('AT-03: missing actual' in e for e in errors))
        self.assertTrue(any('AT-03: evidence' in e for e in errors))

    def test_same_person_install_is_not_independent(self):
        record, blobs = self.fixture()
        record['installed_by'] = record['prepared_by']
        self.assertTrue(any('Independent ZIP installer' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_zip_case_cannot_claim_another_installers_work(self):
        record, blobs = self.fixture()
        record['checks']['AT-16']['tester'] = 'owner'
        self.assertTrue(any('actual independent' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_full_cli_checks_frozen_git_candidate_and_zip(self):
        record, blobs = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            candidate = parent/'candidate'
            candidate.mkdir()
            blobs['docs/acceptance.json'] = json.dumps(self.registry).encode()
            blobs['docs/ISSUES.md'] = (ROOT/'docs/ISSUES.md').read_bytes()
            for name,data in blobs.items():
                path = candidate/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
            def run(*args):
                return subprocess.check_output(['git',*args],cwd=candidate,stderr=subprocess.DEVNULL)
            run('init','--initial-branch=main')
            run('config','core.hooksPath','.git/no-hooks')
            run('config','core.autocrlf','false')  # Deterministic source ZIP, like GitHub.
            run('add','--all')
            run('-c','user.name=Synthetic gate test','-c','user.email=test@example.invalid',
                'commit','-m','test: Create synthetic candidate')
            sha=run('rev-parse','HEAD').decode().strip()
            archive=parent/'candidate.zip'
            archive.write_bytes(run('archive','--format=zip','--prefix=repo-sha/',sha))
            record['tested_commit']=sha
            record['archive_url']=record['repository_url']+'/archive/'+sha+'.zip'
            record['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
            evidence=parent/'evidence.json'
            evidence.write_text(json.dumps(record),encoding='utf-8')
            args=['check_readiness.py','--release','--evidence',str(evidence),'--archive',str(archive)]
            with patch.object(gate,'ROOT',candidate),patch.object(sys,'argv',args),contextlib.redirect_stdout(io.StringIO()) as captured:
                result = gate.main()
                self.assertEqual(result,0,captured.getvalue())  # Metadata/identity only, never an app test.
            # A different ZIP with an updated claimed hash still fails candidate identity.
            with ZipFile(archive,'w') as z:
                z.writestr('repo-sha/results/fixture.md',b'different candidate bytes')
            record['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
            evidence.write_text(json.dumps(record),encoding='utf-8')
            with patch.object(gate,'ROOT',candidate),patch.object(sys,'argv',args),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(),1)

    def test_samples_require_actual_nonempty_assets(self):
        record, blobs = self.fixture()
        blobs.pop('assets/samples/0.wav')
        self.assertTrue(any('audio asset' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_empty_sample_manifest_is_not_ready(self):
        record, blobs = self.fixture()
        blobs['assets/samples/manifest.json'] = b'{"samples":[]}'
        self.assertTrue(any('Three distinct' in e for e in gate.release_errors(self.registry, record, set(blobs), blobs.__getitem__)))

    def test_archive_identity_and_forbidden_extra_file(self):
        blobs = {'README.md':b'right', 'assets/samples/song.wav':b'audio'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'candidate.zip'
            with ZipFile(path,'w') as z:
                for name,data in blobs.items(): z.writestr('repo-sha/'+name,data)
            self.assertEqual(gate.archive_errors(path,set(blobs),blobs.__getitem__), [])
            with ZipFile(path,'w') as z:
                z.writestr('repo-sha/README.md',b'wrong')
                z.writestr('repo-sha/.env',b'dummy placeholder only')
            errors = gate.archive_errors(path,set(blobs),blobs.__getitem__)
            self.assertTrue(any('inventory differs' in e for e in errors))
            self.assertTrue(any('content differs' in e for e in errors))
            self.assertTrue(any('prohibited' in e for e in errors))

    def test_zip_traversal_is_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.zip'
            with ZipFile(path,'w') as z: z.writestr('../escape.txt',b'bad')
            self.assertEqual(gate.archive_errors(path,set(),lambda name:b''), ['ZIP contains unsafe paths'])

    def test_release_cli_without_evidence_is_not_ready(self):
        result = subprocess.run([sys.executable, str(ROOT/'scripts/check_readiness.py'), '--release'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('NOT READY',result.stdout)


if __name__ == '__main__':
    unittest.main()
