"""Private server configuration; status responses never contain values."""
from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from pydantic import SecretStr


ROOT = Path(__file__).resolve().parents[1]
PORTS = {"text": 9001, "art": 9006, "music": 9007, "speech": 9008}


class ConfigurationError(ValueError):
    """A safe diagnostic containing only the affected role, never its value."""


@dataclass(frozen=True)
class ServiceConfig:
    origin: str
    key: SecretStr


@dataclass(frozen=True)
class Settings:
    services: dict[str, ServiceConfig]

    @classmethod
    def load(cls, env_file: Path | None = ROOT / ".env", environ=None):
        values = dict(dotenv_values(env_file, interpolate=False)) if env_file and env_file.is_file() else {}
        values.update(os.environ if environ is None else environ)
        services = {}
        for role, port in PORTS.items():
            prefix = "JUKEBOX_" + role.upper()
            endpoint = (values.get(prefix + "_ENDPOINT") or "").strip()
            key = (values.get(prefix + "_API_KEY") or "").strip()
            # The committed example can be copied unchanged and still launch.
            if endpoint.startswith("REPLACE_"):
                endpoint = ""
            if key.startswith("REPLACE_"):
                key = ""
            if endpoint:
                try:
                    url = urlsplit(endpoint)
                    valid = (url.scheme in {"http", "https"} and url.hostname == "dobolyi.com"
                             and url.port == port and url.username is None and url.password is None
                             and url.path.rstrip("/") in {"", "/v1"}
                             and not url.query and not url.fragment)
                except ValueError:
                    valid = False
                if not valid:
                    raise ConfigurationError(f"Invalid {role} endpoint. Use the documented class host, port and /v1 base URL.")
            if key and any(ord(char) < 32 or ord(char) > 126 for char in key):
                raise ConfigurationError(f"Invalid {role} key format. Check the local environment value.")
            if endpoint and key:
                services[role] = ServiceConfig(f"{url.scheme}://{url.netloc}", SecretStr(key))
        return cls(services)

    def public_status(self):
        return {role: "configured" if role in self.services else "missing" for role in PORTS}
