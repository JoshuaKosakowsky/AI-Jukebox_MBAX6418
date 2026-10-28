"""Launch the actual runtime in a child process; only loopback HTTP is used."""
import json
import os
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import URLError
from urllib.request import urlopen

from jukebox.config import ROOT


def empty_environment():
    env = os.environ.copy()
    for role in ("TEXT", "ART", "MUSIC", "SPEECH"):
        env[f"JUKEBOX_{role}_ENDPOINT"] = "REPLACE_WITH_TEST_ONLY"
        env[f"JUKEBOX_{role}_API_KEY"] = "REPLACE_WITH_TEST_ONLY"
    return env


class LauncherTests(unittest.TestCase):
    def test_actual_module_launch_serves_empty_app_without_credentials(self):
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        process = subprocess.Popen([sys.executable, "-m", "jukebox", "--port", str(port)], cwd=ROOT,
                                   env=empty_environment(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                self.assertIsNone(process.poll(), "Launcher exited before HTTP readiness")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/api/health", timeout=.5) as response:
                        health = json.load(response)
                    break
                except (URLError, TimeoutError):
                    time.sleep(.05)
            else:
                self.fail("Normal launcher did not become ready")
            self.assertEqual(health["status"], "ok")
            with urlopen(f"http://127.0.0.1:{port}/api/status") as response:
                self.assertFalse(json.load(response)["configured"])
            with urlopen(f"http://127.0.0.1:{port}/") as response:
                self.assertIn("Session library", response.read().decode())
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

    def test_invalid_endpoint_exits_without_disclosing_value_or_key(self):
        env = empty_environment()
        env.update(JUKEBOX_TEXT_ENDPOINT="http://private:key@other.example:9001/v1", JUKEBOX_TEXT_API_KEY="private-marker")
        result = subprocess.run([sys.executable, "-m", "jukebox"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid text endpoint", result.stderr)
        self.assertNotIn("private", result.stdout + result.stderr)
        self.assertNotIn("other.example", result.stdout + result.stderr)

    def test_invalid_or_busy_port_produces_actionable_failure(self):
        invalid = subprocess.run([sys.executable, "-m", "jukebox", "--port", "0"], cwd=ROOT, env=empty_environment(), capture_output=True, text=True, timeout=10)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("1024", invalid.stderr)
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            reservation.listen(1)
            port = reservation.getsockname()[1]
            busy = subprocess.run([sys.executable, "-m", "jukebox", "--port", str(port)], cwd=ROOT,
                                  env=empty_environment(), capture_output=True, text=True, timeout=10)
        self.assertNotEqual(busy.returncode, 0)
        self.assertIn(str(port), busy.stderr)
