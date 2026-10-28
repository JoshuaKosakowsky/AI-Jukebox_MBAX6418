"""Cross-platform entrypoint; keep Windows native dependencies out of long paths."""
import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def environment():
    env = os.environ.copy()
    if os.name == "nt" and not env.get("UV_PROJECT_ENVIRONMENT"):
        cache = Path(env.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")))
        checkout = hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
        env["UV_PROJECT_ENVIRONMENT"] = str(cache / "AI-Jukebox_MBAX6418" / checkout)
    env.setdefault("UV_LINK_MODE", "copy")
    return env


def main():
    parser = argparse.ArgumentParser(description="Run/check the locked local jukebox")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Run all offline checks")
    mode.add_argument("--schema", action="store_true", help="Export the shared JSON Schema")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uv = [sys.executable, "-m", "uv"] if importlib.util.find_spec("uv") else [shutil.which("uv") or "uv"]
    if uv == ["uv"]:
        print("Install uv first: python -m pip install uv==0.12.19", file=sys.stderr)
        return 2
    commands = [["-m", "jukebox", "--port", str(args.port)]]
    if args.check:
        commands = [["scripts/verify_repo.py"], ["scripts/check_readiness.py"],
                    ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]]
    elif args.schema:
        commands = [["-m", "jukebox.contracts", "--write", "contracts/app.schema.json"]]
    try:
        for command in commands:
            result = subprocess.run([*uv, "run", "--locked", "python", *command], cwd=ROOT, env=environment())
            if result.returncode:
                return result.returncode
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
