"""Claude marketplace integration for skill installation."""

import subprocess
import sys
from pathlib import Path
from typing import Tuple


class ClaudeMarketplaceManager:
    """Manages Claude plugin marketplace operations."""

    @staticmethod
    def add_skill_to_marketplace(skill_path: Path, skill_name: str) -> Tuple[bool, str]:
        """Launch Claude in headless mode and add skill to marketplace.

        Launches Claude with --dangerously-skip-permissions flag and executes
        the plugin marketplace add command with the skill path.

        Args:
            skill_path: Path to the installed skill directory
            skill_name: Name of the skill being added

        Returns:
            Tuple of (success, message)
        """
        try:
            # Construct Claude command with headless mode and skip permissions
            cmd = [
                sys.executable,
                "-m",
                "claude",
                "headless",
                "--dangerously-skip-permissions",
                "plugin",
                "marketplace",
                "add",
                str(skill_path),
            ]

            # Run subprocess with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                return True, f"Successfully added {skill_name} to Claude marketplace"
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return (
                    False,
                    f"Failed to add {skill_name} to marketplace: {error_msg}",
                )

        except subprocess.TimeoutExpired:
            return (
                False,
                f"Timeout when adding {skill_name} to Claude marketplace",
            )
        except Exception as e:
            return (
                False,
                f"Error adding {skill_name} to marketplace: {e}",
            )
