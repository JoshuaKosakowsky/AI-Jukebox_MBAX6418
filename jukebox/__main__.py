"""Normal local launcher: uv run --locked python -m jukebox."""
import argparse
import sys

from .config import ConfigurationError, Settings


def main():
    parser = argparse.ArgumentParser(description="Start the local AI Jukebox")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    try:
        settings = Settings.load()
    except ConfigurationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    import uvicorn
    from .app import create_app
    print(f"AI Jukebox: http://127.0.0.1:{args.port} (configuration only; no service calls on startup)")
    uvicorn.run(create_app(settings), host="127.0.0.1", port=args.port, access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
