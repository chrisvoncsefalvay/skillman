"""Configuration management for skillman."""

from pathlib import Path
from typing import Optional, Dict, Any
import sys

if sys.version_info >= (3, 11):
    import tomllib

    TOML_LOADS = tomllib.loads
else:
    import tomli as tomllib

    TOML_LOADS = tomllib.loads

import tomli_w


class ConfigManager:
    """Manages ~/.skillman/config.toml configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager."""
        if config_dir is None:
            config_dir = Path.home() / ".skillman"
        self.config_dir = config_dir
        self.config_file = config_dir / "config.toml"

    def _ensure_dir_exists(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _read_config(self) -> Dict[str, Any]:
        """Read current config file."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "rb") as f:
                content = f.read()
            return TOML_LOADS(content.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to parse config file: {e}")

    def _write_config(self, config: Dict[str, Any]):
        """Write config file."""
        self._ensure_dir_exists()
        with open(self.config_file, "w") as f:
            f.write(tomli_w.dumps(config))

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value."""
        config = self._read_config()
        return config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        config = self._read_config()
        config[key] = value
        self._write_config(config)

    def delete(self, key: str) -> bool:
        """Delete configuration value. Returns True if key existed."""
        config = self._read_config()
        if key in config:
            del config[key]
            self._write_config(config)
            return True
        return False

    def list_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._read_config()

    def validate(self):
        """Validate configuration format."""
        try:
            self._read_config()
            return True
        except Exception:
            return False
