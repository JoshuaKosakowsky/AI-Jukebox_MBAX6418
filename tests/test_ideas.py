"""Offline behavior for the local idea generator, not service quality."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SongIdeaTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Optional Node runtime is unavailable")
    def test_actual_idea_controls_preserve_custom_inputs_without_generation(self):
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "tests/frontend_ideas_probe.cjs"),
             str(ROOT / "jukebox/web/ideas.js")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
