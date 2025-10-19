"""Utility funx for skillman."""

import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib

    TOML_LOADS = tomllib.loads
else:
    import tomli as tomllib

    TOML_LOADS = tomllib.loads

from skillman.models import Manifest, LockFile


class ManifestFile:
    """Manages skills.toml manifest file."""

    def __init__(self, manifest_path: Path = Path("skills.toml")):
        """Initialize manifest file manager."""
        self.manifest_path = manifest_path

    def exists(self) -> bool:
        """Check if manifest file exists."""
        return self.manifest_path.exists()

    def create_empty(self) -> Manifest:
        """Create empty manifest."""
        manifest = Manifest()
        self.write(manifest)
        return manifest

    def read(self) -> Manifest:
        """Read manifest from file."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        try:
            content = self.manifest_path.read_text(encoding="utf-8")
            return Manifest.from_toml(content)
        except Exception as e:
            raise ValueError(f"Failed to read manifest: {e}")

    def write(self, manifest: Manifest):
        """Write manifest to file."""
        try:
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            content = manifest.to_toml()
            self.manifest_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to write manifest: {e}")

    def read_or_create(self) -> Manifest:
        """Read manifest or create empty if not exists."""
        if self.exists():
            return self.read()
        return self.create_empty()


class LockFileManager:
    """Manages skills.lock file."""

    def __init__(self, lock_path: Path = Path("skills.lock")):
        """Initialize lock file manager."""
        self.lock_path = lock_path

    def exists(self) -> bool:
        """Check if lock file exists."""
        return self.lock_path.exists()

    def read(self) -> LockFile:
        """Read lock file."""
        if not self.lock_path.exists():
            return LockFile()

        try:
            content = self.lock_path.read_text(encoding="utf-8")
            return LockFile.from_toml(content)
        except Exception as e:
            raise ValueError(f"Failed to read lock file: {e}")

    def write(self, lock_file: LockFile):
        """Write lock file."""
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            content = lock_file.to_toml()
            self.lock_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Failed to write lock file: {e}")

    def read_or_create(self) -> LockFile:
        """Read lock file or create empty if not exists."""
        if self.exists():
            return self.read()
        return LockFile()


def get_skill_description(skill_path: Path) -> Optional[str]:
    """Extract description from SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None

    try:
        content = skill_md.read_text(encoding="utf-8")
        # Extract first non-empty line as description
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line[:100]  # Limit to 100 chars
        return None
    except Exception:
        return None


def parse_status(
    manifest_exists: bool,
    installed_exists: bool,
    manifest_version: Optional[str],
    installed_version: Optional[str],
) -> str:
    """Determine skill status."""
    if not manifest_exists and installed_exists:
        return "orphaned"
    if manifest_exists and not installed_exists:
        return "missing"
    if manifest_exists and installed_exists:
        if manifest_version == installed_version:
            return "synced"
        return "outdated"
    return "unknown"
