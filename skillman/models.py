"""Data models for skillman."""

import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# Handle tomli/tomllib import for different Python versions
if sys.version_info >= (3, 11):
    import tomllib

    TOML_LOADS = tomllib.loads
else:
    import tomli as tomllib

    TOML_LOADS = tomllib.loads

import tomli_w

TOML_DUMPS = tomli_w.dumps


@dataclass
class SkillMetadata:
    """Metadata extracted from SKILL.md front matter."""

    title: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillValidationResult:
    """Result of skill validation."""

    is_valid: bool
    error_message: str = ""
    metadata: Optional[SkillMetadata] = None


@dataclass
class Skill:
    """Represents a single skill definition."""

    name: str
    source: str
    version: str = "latest"
    scope: str = "local"
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate skill configuration."""
        if self.scope not in ("local", "user"):
            raise ValueError(f"Invalid scope: {self.scope}. Must be 'local' or 'user'.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        d = asdict(self)
        return d


@dataclass
class Manifest:
    """Represents skills.toml manifest."""

    version: str = "1.0.0"
    skills: List[Skill] = field(default_factory=list)

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name."""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

    def has_skill(self, name: str) -> bool:
        """Check if skill exists in manifest."""
        return self.get_skill(name) is not None

    def add_skill(self, skill: Skill):
        """Add skill to manifest."""
        if self.has_skill(skill.name):
            raise ValueError(f"Skill '{skill.name}' already exists in manifest.")
        self.skills.append(skill)

    def remove_skill(self, name: str) -> bool:
        """Remove skill from manifest. Returns True if removed, False if not found."""
        for i, skill in enumerate(self.skills):
            if skill.name == name:
                self.skills.pop(i)
                return True
        return False

    @classmethod
    def from_toml(cls, content: str) -> "Manifest":
        """Parse manifest from TOML content."""
        try:
            data = TOML_LOADS(content)
        except Exception as e:
            raise ValueError(f"Failed to parse TOML: {e}")

        tool_data = data.get("tool", {}).get("skillman", {})
        version = tool_data.get("version", "1.0.0")

        skills = []
        for skill_data in tool_data.get("skills", []):
            skill = Skill(
                name=skill_data["name"],
                source=skill_data["source"],
                version=skill_data.get("version", "latest"),
                scope=skill_data.get("scope", "local"),
                aliases=skill_data.get("aliases", []),
            )
            skills.append(skill)

        return cls(version=version, skills=skills)

    def to_toml(self) -> str:
        """Convert manifest to TOML format."""
        data = {
            "tool": {
                "skillman": {
                    "version": self.version,
                    "skills": [asdict(skill) for skill in self.skills],
                }
            }
        }
        return TOML_DUMPS(data)


@dataclass
class LockEntry:
    """Single entry in lock file."""

    name: str
    source: str
    version_spec: str  # What was requested (e.g., @latest, @1.2.3)
    resolved_sha: str  # The actual commit SHA
    resolved_version: str  # The actual version tag


@dataclass
class LockFile:
    """Represents skills.lock for reproducibility."""

    version: str = "1.0.0"
    entries: Dict[str, LockEntry] = field(default_factory=dict)

    def set_entry(
        self,
        name: str,
        source: str,
        version_spec: str,
        resolved_sha: str,
        resolved_version: str,
    ):
        """Set lock entry."""
        self.entries[name] = LockEntry(
            name=name,
            source=source,
            version_spec=version_spec,
            resolved_sha=resolved_sha,
            resolved_version=resolved_version,
        )

    def get_entry(self, name: str) -> Optional[LockEntry]:
        """Get lock entry by name."""
        return self.entries.get(name)

    @classmethod
    def from_toml(cls, content: str) -> "LockFile":
        """Parse lock file from TOML content."""
        try:
            data = TOML_LOADS(content)
        except Exception as e:
            raise ValueError(f"Failed to parse lock file: {e}")

        lock_data = data.get("lock", {})
        version = lock_data.get("version", "1.0.0")

        entries = {}
        for name, entry_data in lock_data.get("entries", {}).items():
            entry = LockEntry(
                name=name,
                source=entry_data["source"],
                version_spec=entry_data["version_spec"],
                resolved_sha=entry_data["resolved_sha"],
                resolved_version=entry_data["resolved_version"],
            )
            entries[name] = entry

        return cls(version=version, entries=entries)

    def to_toml(self) -> str:
        """Convert lock file to TOML format."""
        entries_dict = {}
        for name, entry in self.entries.items():
            entries_dict[name] = {
                "source": entry.source,
                "version_spec": entry.version_spec,
                "resolved_sha": entry.resolved_sha,
                "resolved_version": entry.resolved_version,
            }

        data = {"lock": {"version": self.version, "entries": entries_dict}}
        return TOML_DUMPS(data)
