"""Exercise protected-main guards in an isolated Git repo; never push anywhere."""
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
        cls.git('branch', 'codex/hook-test')
        cls.git('config', 'core.hooksPath', str(HOOKS))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args, check=True):
        return subprocess.run(['git', *args], cwd=cls.repo, env=cls.env,
                              text=True, capture_output=True, check=check)

    def hook(self, name, *, extra_config=(), allow_push=True, ref=None):
        args = ['-c', f'jukebox.allowPush={str(allow_push).lower()}']
        for value in extra_config:
            args.extend(['-c', value])
        args.extend(['hook', 'run'])
        if ref is not None:
            stdin_path = self.repo / 'hook-input'
            stdin_path.write_text(ref + '\n', encoding='utf-8', newline='\n')
            args.append(f'--to-stdin={stdin_path}')
        return self.git(*args, name, check=False)

    def main_update(self, local=None, remote=None):
        return f'refs/heads/main {local or self.second} refs/heads/main {remote or self.first}'

    def task_update(self):
        return f'refs/heads/codex/task {self.second} refs/heads/codex/task {self.first}'

    def assert_blocked(self, result, message):
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn(message, result.stderr)

    def test_main_commit_is_blocked(self):
        self.assert_blocked(self.hook('pre-commit'), 'Commit blocked')

    def test_task_branch_commit_is_allowed(self):
        self.git('switch', 'codex/hook-test')
        try:
            result = self.hook('pre-commit')
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            self.git('switch', 'main')

    def test_removed_setting_cannot_allow_main_commit(self):
        result = self.hook('pre-commit', extra_config=('jukebox.soloSetup=true',))
        self.assert_blocked(result, 'Commit blocked')

    def test_push_requires_publication_authorization(self):
        result = self.hook('pre-push', allow_push=False, ref=self.task_update())
        self.assert_blocked(result, 'local-only')

    def test_main_fast_forward_push_is_blocked(self):
        self.assert_blocked(self.hook('pre-push', ref=self.main_update()), 'main changes require reviewed PRs')

    def test_removed_setting_cannot_allow_main_push(self):
        result = self.hook('pre-push', extra_config=('jukebox.soloSetup=true',), ref=self.main_update())
        self.assert_blocked(result, 'main changes require reviewed PRs')

    def test_main_deletion_is_blocked(self):
        result = self.hook('pre-push', ref=self.main_update(local='0' * 40))
        self.assert_blocked(result, 'no direct update or deletion')

    def test_main_history_rewrite_is_blocked(self):
        result = self.hook('pre-push', ref=self.main_update(local=self.first, remote=self.second))
        self.assert_blocked(result, 'no direct update or deletion')

    def test_task_branch_push_is_allowed(self):
        result = self.hook('pre-push', ref=self.task_update())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_main_push_is_blocked_in_a_batch_with_task_branch(self):
        result = self.hook('pre-push', ref=self.task_update() + '\n' + self.main_update())
        self.assert_blocked(result, 'main changes require reviewed PRs')


if __name__ == '__main__':
    unittest.main()
