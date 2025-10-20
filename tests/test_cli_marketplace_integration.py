"""Integration tests for CLI with Claude marketplace."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from click.testing import CliRunner

import pytest

from skillman.cli import main
from skillman.models import Skill


class TestCliMarketplaceIntegration:
    """Test suite for CLI marketplace integration."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_manifest(self):
        """Mock manifest file."""
        return """
[[skills]]
name = "test-skill"
source = "username/repo"
version = "latest"
scope = "local"
"""

    def test_add_command_calls_marketplace_on_success(self, cli_runner):
        """Test that add command calls marketplace manager on successful installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                # Mock all the required components
                with (
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.SkillValidator.validate") as mock_validate,
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                    patch("skillman.cli.ConfigManager") as mock_config,
                ):

                    # Setup mocks
                    mock_spec = MagicMock()
                    mock_spec.repo = "test-skill"
                    mock_spec.version = "latest"
                    mock_spec_class.return_value = mock_spec

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "abc123",
                    )
                    mock_github_class.return_value = mock_github

                    mock_validate.return_value = MagicMock(is_valid=True)

                    mock_install.return_value = (True, "Skill installed successfully")

                    mock_get_path.return_value = Path("/claude/skills/test-skill")

                    mock_manifest = MagicMock()
                    mock_manifest.has_skill.return_value = False
                    mock_manifest_file.return_value.read_or_create.return_value = (
                        mock_manifest
                    )

                    mock_marketplace.return_value = (
                        True,
                        "Successfully added test-skill to Claude marketplace",
                    )

                    # Run add command with dangerously-skip-permissions
                    result = cli_runner.invoke(
                        main,
                        [
                            "add",
                            "username/repo",
                            "-s",
                            "local",
                            "--dangerously-skip-permissions",
                            "--no-verify",
                        ],
                    )

                    # Verify marketplace manager was called
                    mock_marketplace.assert_called_once()
                    call_args = mock_marketplace.call_args[0]
                    assert call_args[0] == Path("/claude/skills/test-skill")
                    assert call_args[1] == "test-skill"

    def test_add_command_shows_marketplace_success(self, cli_runner):
        """Test that add command displays marketplace success message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                with (
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.SkillValidator.validate") as mock_validate,
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                    patch("skillman.cli.ConfigManager") as mock_config,
                ):

                    # Setup mocks
                    mock_spec = MagicMock()
                    mock_spec.repo = "test-skill"
                    mock_spec.version = "latest"
                    mock_spec.__str__.return_value = "username/repo"
                    mock_spec_class.return_value = mock_spec

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "abc123",
                    )
                    mock_github_class.return_value = mock_github

                    mock_validate.return_value = MagicMock(is_valid=True)
                    mock_install.return_value = (True, "Skill installed successfully")
                    mock_get_path.return_value = Path("/claude/skills/test-skill")

                    mock_manifest = MagicMock()
                    mock_manifest.has_skill.return_value = False
                    mock_manifest_file.return_value.read_or_create.return_value = (
                        mock_manifest
                    )

                    mock_marketplace.return_value = (
                        True,
                        "Successfully added test-skill to Claude marketplace",
                    )

                    result = cli_runner.invoke(
                        main,
                        [
                            "add",
                            "username/repo",
                            "-s",
                            "local",
                            "--dangerously-skip-permissions",
                            "--no-verify",
                        ],
                    )

                    # Verify success message is displayed
                    assert (
                        "Successfully added test-skill to Claude marketplace"
                        in result.output
                    )

    def test_add_command_shows_marketplace_failure_as_warning(self, cli_runner):
        """Test that add command shows marketplace failure as warning but doesn't fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                with (
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.SkillValidator.validate") as mock_validate,
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                    patch("skillman.cli.ConfigManager") as mock_config,
                ):

                    # Setup mocks
                    mock_spec = MagicMock()
                    mock_spec.repo = "test-skill"
                    mock_spec.version = "latest"
                    mock_spec.__str__.return_value = "username/repo"
                    mock_spec_class.return_value = mock_spec

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "abc123",
                    )
                    mock_github_class.return_value = mock_github

                    mock_validate.return_value = MagicMock(is_valid=True)
                    mock_install.return_value = (True, "Skill installed successfully")
                    mock_get_path.return_value = Path("/claude/skills/test-skill")

                    mock_manifest = MagicMock()
                    mock_manifest.has_skill.return_value = False
                    mock_manifest_file.return_value.read_or_create.return_value = (
                        mock_manifest
                    )

                    # Marketplace returns failure
                    mock_marketplace.return_value = (
                        False,
                        "Failed to register skill with marketplace",
                    )

                    result = cli_runner.invoke(
                        main,
                        [
                            "add",
                            "username/repo",
                            "-s",
                            "local",
                            "--dangerously-skip-permissions",
                            "--no-verify",
                        ],
                    )

                    # Verify failure message is shown but command still succeeds
                    assert "Failed to register skill with marketplace" in result.output
                    assert result.exit_code == 0

    def test_add_command_handles_no_installed_path(self, cli_runner):
        """Test that add command handles case where get_skill_path returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                with (
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.SkillValidator.validate") as mock_validate,
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                    patch("skillman.cli.ConfigManager") as mock_config,
                ):

                    # Setup mocks
                    mock_spec = MagicMock()
                    mock_spec.repo = "test-skill"
                    mock_spec.version = "latest"
                    mock_spec.__str__.return_value = "username/repo"
                    mock_spec_class.return_value = mock_spec

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "abc123",
                    )
                    mock_github_class.return_value = mock_github

                    mock_validate.return_value = MagicMock(is_valid=True)
                    mock_install.return_value = (True, "Skill installed successfully")
                    mock_get_path.return_value = None  # Simulate no installed path

                    mock_manifest = MagicMock()
                    mock_manifest.has_skill.return_value = False
                    mock_manifest_file.return_value.read_or_create.return_value = (
                        mock_manifest
                    )

                    result = cli_runner.invoke(
                        main,
                        [
                            "add",
                            "username/repo",
                            "-s",
                            "local",
                            "--dangerously-skip-permissions",
                            "--no-verify",
                        ],
                    )

                    # Verify marketplace was not called
                    mock_marketplace.assert_not_called()
                    # But add command should still succeed
                    assert result.exit_code == 0

    def test_update_command_calls_marketplace(self, cli_runner):
        """Test that update command calls marketplace manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                with (
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.ConfigManager") as mock_config,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                ):

                    # Setup mocks
                    mock_skill = MagicMock()
                    mock_skill.name = "test-skill"
                    mock_skill.source = "username/repo"
                    mock_skill.version = "1.0.0"
                    mock_skill.scope = "local"

                    mock_manifest = MagicMock()
                    mock_manifest.skills = [mock_skill]
                    mock_manifest.get_skill.return_value = mock_skill
                    mock_manifest_file.return_value.exists.return_value = True
                    mock_manifest_file.return_value.read.return_value = mock_manifest

                    mock_spec = MagicMock()
                    mock_spec_class.return_value = mock_spec

                    mock_config.return_value.get.return_value = None

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "def456",
                    )
                    mock_github_class.return_value = mock_github

                    mock_install.return_value = (True, "Skill updated")
                    mock_get_path.return_value = Path("/claude/skills/test-skill")
                    mock_marketplace.return_value = (True, "Successfully added")

                    result = cli_runner.invoke(main, ["update", "test-skill"])

                    # Verify marketplace manager was called
                    mock_marketplace.assert_called_once()

    def test_sync_command_calls_marketplace(self, cli_runner):
        """Test that sync command calls marketplace manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with cli_runner.isolated_filesystem(temp_dir=tmpdir):
                with (
                    patch("skillman.cli.ManifestFile") as mock_manifest_file,
                    patch("skillman.cli.SkillSpec") as mock_spec_class,
                    patch("skillman.cli.ConfigManager") as mock_config,
                    patch("skillman.cli.GitHubClient") as mock_github_class,
                    patch("skillman.cli.SkillInstaller.install_skill") as mock_install,
                    patch(
                        "skillman.cli.SkillInstaller.get_skill_path"
                    ) as mock_get_path,
                    patch("skillman.cli.LockFileManager") as mock_lock_manager,
                    patch(
                        "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace"
                    ) as mock_marketplace,
                ):

                    # Setup mocks
                    mock_skill = MagicMock()
                    mock_skill.name = "test-skill"
                    mock_skill.source = "username/repo"
                    mock_skill.version = "1.0.0"
                    mock_skill.scope = "local"

                    mock_manifest = MagicMock()
                    mock_manifest.skills = [mock_skill]
                    mock_manifest.has_skill.return_value = False
                    mock_manifest_file.return_value.read_or_create.return_value = (
                        mock_manifest
                    )

                    mock_spec = MagicMock()
                    mock_spec_class.return_value = mock_spec

                    mock_config.return_value.get.return_value = None

                    mock_github = MagicMock()
                    mock_github.fetch_skill.return_value = (
                        Path("/tmp/skill"),
                        "ghi789",
                    )
                    mock_github_class.return_value = mock_github

                    mock_install.return_value = (True, "Skill installed")
                    # First call (checking if skill is installed) returns None,
                    # second call (after installation) returns the path
                    mock_get_path.side_effect = [
                        None,
                        Path("/claude/skills/test-skill"),
                    ]
                    mock_marketplace.return_value = (True, "Successfully added")

                    result = cli_runner.invoke(main, ["sync"])

                    # Verify marketplace manager was called
                    mock_marketplace.assert_called()
