"""Exercise team guards and the explicit solo exception in an isolated Git repo."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


HOOKS = Path(__file__).resolve().parents[1] / '.githooks'


class GitHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.temp.name)
        cls.env = os.environ.copy()
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            cls.env.pop(key, None)
        cls.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        cls.git('init', '--initial-branch=main')
        for message in ('first', 'second'):
            cls.git('-c', 'user.name=Hook Test', '-c', 'user.email=hooks@example.invalid',
                    'commit', '--allow-empty', '-m', message)
            setattr(cls, message, cls.git('rev-parse', 'HEAD').stdout.strip())
        cls.git('config', 'core.hooksPath', str(HOOKS))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args, check=True):
        return subprocess.run(['git', *args], cwd=cls.repo, env=cls.env,
                              text=True, capture_output=True, check=check)

    def hook(self, name, *, solo=False, allow_push=True, ref=None):
        args = ['-c', f'jukebox.soloSetup={str(solo).lower()}',
                '-c', f'jukebox.allowPush={str(allow_push).lower()}', 'hook', 'run']
        if ref is not None:
            stdin_path = self.repo / 'hook-input'
            stdin_path.write_text(ref + '\n', encoding='utf-8', newline='\n')
            args.append(f'--to-stdin={stdin_path}')
        return self.git(*args, name, check=False)

    def main_update(self, local=None, remote=None):
        return f'refs/heads/main {local or self.second} refs/heads/main {remote or self.first}'

    def test_team_main_commit_is_blocked(self):
        result = self.hook('pre-commit')
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn('Commit blocked', result.stderr)

    def test_explicit_solo_commit_is_allowed_without_persisting_option(self):
        result = self.hook('pre-commit', solo=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('config', '--get', 'jukebox.soloSetup', check=False).returncode, 1)

    def test_push_still_requires_publication_authorization(self):
        result = self.hook('pre-push', solo=True, allow_push=False, ref=self.main_update())
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn('local-only', result.stderr)

    def test_team_main_push_is_blocked(self):
        result = self.hook('pre-push', ref=self.main_update())
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn('team main updates require PRs', result.stderr)

    def test_solo_fast_forward_is_allowed(self):
        result = self.hook('pre-push', solo=True, ref=self.main_update())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_solo_main_deletion_is_blocked(self):
        result = self.hook('pre-push', solo=True, ref=self.main_update(local='0' * 40))
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn('deletion is forbidden', result.stderr)

    def test_solo_non_fast_forward_is_blocked(self):
        result = self.hook('pre-push', solo=True,
                           ref=self.main_update(local=self.first, remote=self.second))
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn('only fast-forward', result.stderr)

    def test_team_task_branch_push_is_allowed(self):
        ref = f'refs/heads/codex/task {self.second} refs/heads/codex/task {self.first}'
        result = self.hook('pre-push', ref=ref)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
