"""GitHub integration for skillman."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import yaml

from skillman.models import SkillMetadata, SkillValidationResult


class SkillSpec:
    """Parse skill specification: username/repo[@version] or username/repo/folder/subfolder/...[@version]"""

    def __init__(self, spec: str):
        """Parse skill specification."""
        # Split version from spec
        if "@" in spec:
            self.spec_without_version = spec.rsplit("@", 1)[0]
            self.version = spec.rsplit("@", 1)[1]
        else:
            self.spec_without_version = spec
            self.version = "latest"

        # Parse repository and folder
        parts = self.spec_without_version.split("/")
        if len(parts) < 2:
            raise ValueError(
                f"Invalid skill spec: {spec}. Expected 'username/repo' or 'username/repo/folder/...'."
            )

        self.username = parts[0]
        self.repo = parts[1]
        # Support arbitrary nesting: join all remaining parts as folder path
        self.folder = "/".join(parts[2:]) if len(parts) > 2 else None

    @property
    def repo_url(self) -> str:
        """Get GitHub repository URL."""
        return f"https://github.com/{self.username}/{self.repo}"

    @property
    def skill_path(self) -> str:
        """Get skill path within repository."""
        return self.folder if self.folder else "."

    def __str__(self) -> str:
        """String representation."""
        if self.folder:
            return f"{self.username}/{self.repo}/{self.folder}@{self.version}"
        return f"{self.username}/{self.repo}@{self.version}"


class GitHubClient:
    """Client for GitHub operations."""

    def __init__(self, github_token: Optional[str] = None):
        """Initialize GitHub client."""
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")

    def _get_git_auth_args(self) -> list:
        """Get git authentication arguments."""
        if not self.github_token:
            return []
        # For HTTPS URLs, we need to use credential helper or URL rewriting
        return []

    def _clone_repo(self, repo_url: str, version: str, target_dir: Path) -> str:
        """Clone repository and return resolved commit SHA."""
        try:
            # Clone with depth 1 for latest, or full clone for specific versions
            if version == "latest":
                cmd = ["git", "clone", "--depth", "1", repo_url, str(target_dir)]
            else:
                cmd = ["git", "clone", repo_url, str(target_dir)]

            # Add auth if token is available
            if self.github_token:
                # Inject token into URL
                parsed = urlparse(repo_url)
                repo_url_with_auth = f"https://oauth2:{self.github_token}@github.com/{parsed.path.lstrip('/')}"
                cmd[cmd.index(repo_url)] = repo_url_with_auth

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")

            # Checkout specific version if needed
            if version != "latest":
                try:
                    # Try as tag first
                    cmd = ["git", "-C", str(target_dir), "checkout", version]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=60
                    )
                    if result.returncode != 0:
                        raise RuntimeError(
                            f"Failed to checkout {version}: {result.stderr}"
                        )
                except Exception as e:
                    raise RuntimeError(f"Failed to checkout version {version}: {e}")

            # Get current commit SHA
            cmd = ["git", "-C", str(target_dir), "rev-parse", "HEAD"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to get commit SHA: {result.stderr}")

            resolved_sha = result.stdout.strip()

            # Get version tag if checking out a tag
            if version != "latest":
                try:
                    cmd = [
                        "git",
                        "-C",
                        str(target_dir),
                        "describe",
                        "--tags",
                        "--exact-match",
                    ]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=60
                    )
                    if result.returncode == 0:
                        pass  # Version tag resolved successfully
                except Exception:
                    pass

            return resolved_sha

        except Exception as e:
            # Cleanup on failure
            if target_dir.exists():
                shutil.rmtree(target_dir)
            raise RuntimeError(f"Failed to clone repository: {e}")

    def fetch_skill(
        self, spec: SkillSpec, target_dir: Optional[Path] = None
    ) -> Tuple[Path, str]:
        """Fetch skill from GitHub.

        Returns tuple of (skill_path, resolved_sha).
        """
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix="skillman_"))

        # Clone repository
        resolved_sha = self._clone_repo(spec.repo_url, spec.version, target_dir)

        # Get skill path
        skill_path = target_dir / spec.skill_path
        if not skill_path.exists():
            shutil.rmtree(target_dir)
            raise ValueError(f"Skill path '{spec.skill_path}' not found in repository")

        return skill_path, resolved_sha


class SkillValidator:
    """Validates skill structure and extracts metadata."""

    @staticmethod
    def _parse_yaml_frontmatter(content: str) -> Tuple[Optional[dict], str]:
        """Parse YAML front matter from markdown.

        Returns tuple of (yaml_dict, remaining_content).
        """
        if not content.startswith("---"):
            return None, content

        # Find closing ---
        lines = content.split("\n")
        if len(lines) < 3:
            return None, content

        # Look for closing --- on line 2 or later
        closing_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_index = i
                break

        if closing_index is None:
            return None, content

        # Parse YAML
        yaml_content = "\n".join(lines[1:closing_index])
        try:
            yaml_dict = yaml.safe_load(yaml_content) or {}
            remaining = "\n".join(lines[closing_index + 1:])
            return yaml_dict, remaining
        except Exception:
            return None, content

    @staticmethod
    def _extract_metadata(
        skill_path: Path, yaml_dict: Optional[dict], content: str
    ) -> SkillMetadata:
        """Extract metadata from YAML front matter and content."""
        metadata = SkillMetadata()

        if yaml_dict:
            metadata.title = yaml_dict.get("title")
            metadata.description = yaml_dict.get("description")
            metadata.license = yaml_dict.get("license")
            metadata.author = yaml_dict.get("author")
            metadata.version = yaml_dict.get("version")
            metadata.tags = yaml_dict.get("tags", [])

            # Store any extra fields
            known_fields = {
                "title",
                "description",
                "license",
                "author",
                "version",
                "tags",
            }
            metadata.extra = {
                k: v for k, v in yaml_dict.items() if k not in known_fields
            }

        # If no description from YAML, try to extract first paragraph from markdown
        if not metadata.description and content.strip():
            for line in content.split("\n"):
                line = line.strip()
                # Skip markdown headers and empty lines
                if line and not line.startswith("#"):
                    metadata.description = line[:200]  # Limit to 200 chars
                    break

        return metadata

    @staticmethod
    def validate(skill_path: Path) -> SkillValidationResult:
        """Validate skill structure and extract metadata.

        Returns SkillValidationResult with validation status and metadata.
        """
        if not skill_path.is_dir():
            return SkillValidationResult(
                is_valid=False,
                error_message=f"Skill path is not a directory: {skill_path}",
            )

        # Check for SKILL.md
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return SkillValidationResult(
                is_valid=False, error_message="Skill must contain SKILL.md in root"
            )

        # Check for readable content and parse metadata
        try:
            content = skill_md.read_text(encoding="utf-8")
            if not content.strip():
                return SkillValidationResult(
                    is_valid=False, error_message="SKILL.md is empty"
                )

            # Parse YAML front matter
            yaml_dict, remaining_content = SkillValidator._parse_yaml_frontmatter(
                content
            )

            # Extract metadata
            metadata = SkillValidator._extract_metadata(
                skill_path, yaml_dict, remaining_content
            )

            return SkillValidationResult(
                is_valid=True, error_message="", metadata=metadata
            )

        except Exception as e:
            return SkillValidationResult(
                is_valid=False, error_message=f"Failed to read SKILL.md: {e}"
            )
