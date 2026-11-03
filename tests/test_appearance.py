"""Offline behavioral check for visual preferences; no service calls."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AppearanceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Optional Node runtime is unavailable")
    def test_preferences_do_not_generate_or_rebuild_media(self):
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "tests/frontend_appearance_probe.cjs"),
             str(ROOT / "jukebox/web/appearance.js")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
