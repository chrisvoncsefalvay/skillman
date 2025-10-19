"""Installation engine for skills."""

import shutil
from pathlib import Path
from typing import Optional, List, Tuple
import tempfile
import os


class SkillInstaller:
    """Manages skill installation."""

    # Directories and patterns to exclude during installation
    IGNORE_PATTERNS = {
        ".git",
        ".github",
        ".gitignore",
        ".gitattributes",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        "*.egg-info",
        ".DS_Store",
        "Thumbs.db",
    }

    @staticmethod
    def _ignore_patterns(directory: str, contents: List[str]) -> set:
        """Return set of files/directories to ignore during copy.

        Used with shutil.copytree's ignore parameter.
        """
        ignored = set()
        for name in contents:
            # Check exact matches
            if name in SkillInstaller.IGNORE_PATTERNS:
                ignored.add(name)
            # Check pattern matches
            else:
                for pattern in SkillInstaller.IGNORE_PATTERNS:
                    if pattern.startswith("*") and name.endswith(pattern[1:]):
                        ignored.add(name)
                        break
        return ignored

    @staticmethod
    def _remove_readonly(func, path, excinfo):
        """Error handler for shutil operations to handle read-only files."""
        import stat

        try:
            if not os.access(path, os.W_OK):
                # Add write permissions and retry
                os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
                func(path)
            else:
                raise excinfo[1]
        except Exception:
            # If all else fails, just skip it
            pass

    @staticmethod
    def get_install_path(scope: str) -> Path:
        """Get installation path for given scope."""
        if scope == "user":
            return Path.home() / ".claude" / "skills" / "user"
        elif scope == "local":
            return Path.cwd() / ".claude" / "skills"
        else:
            raise ValueError(f"Invalid scope: {scope}")

    @staticmethod
    def install_skill(
        skill_path: Path, skill_name: str, scope: str, force: bool = False
    ) -> Tuple[bool, str]:
        """Install skill to target location.

        Returns tuple of (success, message).
        """
        install_path = SkillInstaller.get_install_path(scope)
        target_path = install_path / skill_name

        # Check if already exists
        if target_path.exists() and not force:
            return (
                False,
                f"Skill already installed at {target_path}. Use --force to overwrite.",
            )

        try:
            # Create temp directory for atomic operation
            with tempfile.TemporaryDirectory(prefix="skillman_install_") as temp_dir:
                temp_path = Path(temp_dir) / skill_name

                # Copy skill to temp location, ignoring unnecessary directories
                if skill_path.is_dir():
                    shutil.copytree(
                        skill_path,
                        temp_path,
                        ignore=SkillInstaller._ignore_patterns,
                        dirs_exist_ok=False,
                    )
                else:
                    temp_path.mkdir(parents=True)
                    for item in skill_path.iterdir():
                        if item.is_file():
                            shutil.copy2(item, temp_path)
                        elif (
                            item.is_dir()
                            and item.name not in SkillInstaller.IGNORE_PATTERNS
                        ):
                            shutil.copytree(
                                item,
                                temp_path / item.name,
                                ignore=SkillInstaller._ignore_patterns,
                            )

                # Remove existing if forcing
                if target_path.exists():
                    shutil.rmtree(target_path, onerror=SkillInstaller._remove_readonly)

                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Move from temp to final location
                shutil.move(str(temp_path), str(target_path))

            return True, f"Skill installed to {target_path}"

        except Exception as e:
            # Cleanup on failure
            if target_path.exists():
                try:
                    shutil.rmtree(target_path, onerror=SkillInstaller._remove_readonly)
                except Exception:
                    pass
            return False, f"Installation failed: {e}"

    @staticmethod
    def uninstall_skill(skill_name: str, scope: str) -> Tuple[bool, str]:
        """Uninstall skill from target location.

        Returns tuple of (success, message).
        """
        install_path = SkillInstaller.get_install_path(scope)
        target_path = install_path / skill_name

        if not target_path.exists():
            return False, f"Skill not found at {target_path}"

        try:
            shutil.rmtree(target_path, onerror=SkillInstaller._remove_readonly)
            return True, f"Skill uninstalled from {target_path}"
        except Exception as e:
            return False, f"Uninstall failed: {e}"

    @staticmethod
    def list_installed_skills(scope: Optional[str] = None) -> List[Tuple[str, Path]]:
        """List installed skills in given scope(s).

        Returns list of (skill_name, skill_path) tuples.
        """
        skills = []

        scopes = [scope] if scope else ["local", "user"]
        for s in scopes:
            try:
                install_path = SkillInstaller.get_install_path(s)
                if install_path.exists():
                    for item in install_path.iterdir():
                        if item.is_dir():
                            skills.append((item.name, item))
            except Exception:
                pass

        return skills

    @staticmethod
    def skill_exists(skill_name: str, scope: Optional[str] = None) -> bool:
        """Check if skill is installed."""
        installed = SkillInstaller.list_installed_skills(scope)
        return any(name == skill_name for name, _ in installed)

    @staticmethod
    def get_skill_path(skill_name: str, scope: Optional[str] = None) -> Optional[Path]:
        """Get path to installed skill."""
        installed = SkillInstaller.list_installed_skills(scope)
        for name, path in installed:
            if name == skill_name:
                return path
        return None
