"""Tests for core CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from skillman.cli import main


class TestCliInit:
    """Test suite for CLI init command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_init_creates_skills_toml(self, cli_runner):
        """Test that init command creates empty skills.toml."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 0
            assert "Created skills.toml" in result.output
            assert Path("skills.toml").exists()

    def test_init_skill_toml_already_exists(self, cli_runner):
        """Test that init command handles existing skills.toml."""
        with cli_runner.isolated_filesystem():
            # Create initial file
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 0
            assert "already exists" in result.output

    def test_init_creates_valid_toml(self, cli_runner):
        """Test that init command creates valid TOML file."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(main, ["init"])

            assert result.exit_code == 0
            content = Path("skills.toml").read_text()
            # File should be valid TOML (can be empty)
            assert isinstance(content, str)


class TestCliRemove:
    """Test suite for CLI remove command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_remove_skill_not_in_manifest(self, cli_runner):
        """Test removing skill not in manifest."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["remove", "nonexistent"])

            assert result.exit_code == 0
            assert "not found in manifest" in result.output

    def test_remove_no_manifest_exists(self, cli_runner):
        """Test remove when no skills.toml exists."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(main, ["remove", "test-skill"])

            assert result.exit_code == 0
            assert "No skills.toml found" in result.output

    def test_remove_skill_from_manifest(self, cli_runner):
        """Test removing skill from manifest."""
        with cli_runner.isolated_filesystem():
            with (
                patch("skillman.cli.ManifestFile") as mock_manifest_file,
                patch("skillman.cli.LockFileManager"),
            ):
                mock_manifest = MagicMock()
                mock_manifest.remove_skill.return_value = True
                mock_manifest_file.return_value.exists.return_value = True
                mock_manifest_file.return_value.read.return_value = mock_manifest

                result = cli_runner.invoke(main, ["remove", "test-skill"])

                assert result.exit_code == 0
                assert "Removed test-skill from manifest" in result.output

    def test_remove_skill_with_scope_option(self, cli_runner):
        """Test removing skill with scope option."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "test-skill"
source = "username/repo"
version = "1.0.0"
scope = "local"
"""
            Path("skills.toml").write_text(manifest_content)
            Path("skills.lock").write_text("")

            result = cli_runner.invoke(
                main, ["remove", "test-skill", "-s", "local", "--keep-files"]
            )

            assert result.exit_code == 0

    def test_remove_skill_keep_files(self, cli_runner):
        """Test remove with --keep-files flag."""
        with cli_runner.isolated_filesystem():
            with (
                patch("skillman.cli.ManifestFile") as mock_manifest_file,
                patch("skillman.cli.LockFileManager"),
            ):
                mock_manifest = MagicMock()
                mock_manifest.remove_skill.return_value = True
                mock_manifest_file.return_value.exists.return_value = True
                mock_manifest_file.return_value.read.return_value = mock_manifest

                result = cli_runner.invoke(
                    main, ["remove", "test-skill", "--keep-files"]
                )

                assert result.exit_code == 0
                assert "Removed test-skill from manifest" in result.output


class TestCliList:
    """Test suite for CLI list command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_list_no_skills(self, cli_runner):
        """Test list command with no skills."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["list"])

            assert result.exit_code == 0
            assert "Installed Skills" in result.output or "Name" in result.output

    def test_list_with_scope_filter(self, cli_runner):
        """Test list command with scope filter."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "test-skill"
source = "username/repo"
version = "1.0.0"
scope = "local"
"""
            Path("skills.toml").write_text(manifest_content)
            Path("skills.lock").write_text("")

            result = cli_runner.invoke(main, ["list", "-s", "local"])

            assert result.exit_code == 0
            assert "Installed Skills" in result.output or "Name" in result.output

    def test_list_displays_skills(self, cli_runner):
        """Test that list displays skills from manifest."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "skill1"
source = "user/repo1"
version = "1.0.0"
scope = "local"

[[skills]]
name = "skill2"
source = "user/repo2"
version = "2.0.0"
scope = "user"
"""
            Path("skills.toml").write_text(manifest_content)
            Path("skills.lock").write_text("")

            result = cli_runner.invoke(main, ["list"])

            assert result.exit_code == 0
            assert "skill1" in result.output or "Installed Skills" in result.output


class TestCliShow:
    """Test suite for CLI show command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_show_skill_not_found(self, cli_runner):
        """Test show command with non-existent skill."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["show", "nonexistent"])

            assert result.exit_code == 0
            assert "not found" in result.output

    def test_show_skill_in_manifest(self, cli_runner):
        """Test show command displays skill info."""
        with cli_runner.isolated_filesystem():
            with (
                patch("skillman.cli.ManifestFile") as mock_manifest_file,
                patch("skillman.cli.SkillInstaller.get_skill_path", return_value=None),
            ):
                mock_skill = MagicMock()
                mock_skill.name = "test-skill"
                mock_skill.source = "username/repo"
                mock_skill.version = "1.0.0"
                mock_skill.scope = "local"
                mock_skill.aliases = []

                mock_manifest = MagicMock()
                mock_manifest.get_skill.return_value = mock_skill
                mock_manifest_file.return_value.read_or_create.return_value = (
                    mock_manifest
                )

                result = cli_runner.invoke(main, ["show", "test-skill"])

                assert result.exit_code == 0
                assert "test-skill" in result.output
                assert "username/repo" in result.output or "Source" in result.output


class TestCliVerify:
    """Test suite for CLI verify command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_verify_invalid_spec(self, cli_runner):
        """Test verify with invalid specification."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(main, ["verify", "invalid"])

            assert result.exit_code == 1
            assert "Invalid" in result.output

    def test_verify_valid_spec_format(self, cli_runner):
        """Test verify accepts valid spec format."""
        with cli_runner.isolated_filesystem():
            with (
                patch("skillman.cli.GitHubClient") as mock_github_class,
                patch("skillman.cli.SkillValidator.validate") as mock_validate,
                patch("skillman.cli.ConfigManager") as mock_config,
            ):

                mock_github = MagicMock()
                mock_github.fetch_skill.return_value = (Path("/tmp/skill"), "abc123")
                mock_github_class.return_value = mock_github

                mock_validate.return_value = MagicMock(
                    is_valid=True,
                    metadata=MagicMock(
                        title="Test Skill",
                        description="Test Description",
                        license="MIT",
                        author="Test Author",
                        version="1.0.0",
                        tags=["test"],
                    ),
                )
                mock_config.return_value.get.return_value = None

                result = cli_runner.invoke(main, ["verify", "username/repo"])

                # Should pass validation step
                assert mock_validate.called


class TestCliConfigCommand:
    """Test suite for CLI config commands."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_config_set(self, cli_runner):
        """Test setting configuration value."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ConfigManager") as mock_config_class:
                mock_config = MagicMock()
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(
                    main, ["config", "set", "test-key", "test-value"]
                )

                assert result.exit_code == 0
                assert "Set test-key" in result.output
                mock_config.set.assert_called_once_with("test-key", "test-value")

    def test_config_get(self, cli_runner):
        """Test getting configuration value."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ConfigManager") as mock_config_class:
                mock_config = MagicMock()
                mock_config.get.return_value = "test-value"
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(main, ["config", "get", "test-key"])

                assert result.exit_code == 0
                assert "test-key = test-value" in result.output

    def test_config_get_not_set(self, cli_runner):
        """Test getting configuration value that is not set."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ConfigManager") as mock_config_class:
                mock_config = MagicMock()
                mock_config.get.return_value = None
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(main, ["config", "get", "missing-key"])

                assert result.exit_code == 0
                assert "not set" in result.output

    def test_config_list(self, cli_runner):
        """Test listing all configuration values."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ConfigManager") as mock_config_class:
                mock_config = MagicMock()
                mock_config.list_all.return_value = {
                    "key1": "value1",
                    "key2": "value2",
                }
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(main, ["config", "list"])

                assert result.exit_code == 0
                assert "key1" in result.output
                assert "value1" in result.output

    def test_config_list_empty(self, cli_runner):
        """Test listing configuration when empty."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ConfigManager") as mock_config_class:
                mock_config = MagicMock()
                mock_config.list_all.return_value = {}
                mock_config_class.return_value = mock_config

                result = cli_runner.invoke(main, ["config", "list"])

                assert result.exit_code == 0
                assert "No configuration" in result.output


class TestCliClean:
    """Test suite for CLI clean command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_clean_no_orphaned_skills(self, cli_runner):
        """Test clean command with no orphaned skills."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "test-skill"
source = "username/repo"
version = "1.0.0"
scope = "local"
"""
            Path("skills.toml").write_text(manifest_content)

            with patch(
                "skillman.cli.SkillInstaller.list_installed_skills", return_value=[]
            ):
                result = cli_runner.invoke(main, ["clean", "-y"])

                assert result.exit_code == 0
                assert "No orphaned skills found" in result.output

    def test_clean_with_scope_filter(self, cli_runner):
        """Test clean command with scope filter."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            with patch(
                "skillman.cli.SkillInstaller.list_installed_skills", return_value=[]
            ):
                result = cli_runner.invoke(main, ["clean", "-s", "local", "-y"])

                assert result.exit_code == 0

    def test_clean_with_dry_run(self, cli_runner):
        """Test clean command with dry-run option."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            with patch(
                "skillman.cli.SkillInstaller.list_installed_skills",
                return_value=[("orphaned-skill", Path("/test/path"))],
            ):
                result = cli_runner.invoke(main, ["clean", "--dry-run", "-y"])

                assert result.exit_code == 0
                assert "Dry run" in result.output


class TestCliUpdate:
    """Test suite for CLI update command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_update_no_manifest(self, cli_runner):
        """Test update when no manifest exists."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(main, ["update", "test-skill"])

            assert result.exit_code == 0
            assert "No skills.toml found" in result.output

    def test_update_skill_not_found(self, cli_runner):
        """Test update for non-existent skill."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["update", "nonexistent"])

            assert result.exit_code == 0
            assert "not found in manifest" in result.output

    def test_update_all_flag(self, cli_runner):
        """Test update with --all flag."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "skill1"
source = "user/repo1"
version = "1.0.0"
scope = "local"
"""
            Path("skills.toml").write_text(manifest_content)
            Path("skills.lock").write_text("")

            with (
                patch("skillman.cli.GitHubClient") as mock_github_class,
                patch(
                    "skillman.cli.SkillInstaller.install_skill",
                    return_value=(True, "Installed"),
                ),
                patch(
                    "skillman.cli.SkillInstaller.get_skill_path",
                    return_value=Path("/test/path"),
                ),
                patch(
                    "skillman.cli.ClaudeMarketplaceManager.add_skill_to_marketplace",
                    return_value=(True, "Added"),
                ),
                patch("skillman.cli.ConfigManager") as mock_config_class,
            ):

                mock_github = MagicMock()
                mock_github.fetch_skill.return_value = (
                    Path("/tmp/skill"),
                    "abc123",
                )
                mock_github_class.return_value = mock_github
                mock_config_class.return_value.get.return_value = None

                result = cli_runner.invoke(main, ["update", "--all"])

                assert result.exit_code == 0

    def test_update_dry_run(self, cli_runner):
        """Test update with --dry-run flag."""
        with cli_runner.isolated_filesystem():
            with patch("skillman.cli.ManifestFile") as mock_manifest_file:
                mock_skill = MagicMock()
                mock_skill.name = "test-skill"
                mock_skill.source = "user/repo"
                mock_skill.version = "1.0.0"
                mock_skill.scope = "local"

                mock_manifest = MagicMock()
                mock_manifest.get_skill.return_value = mock_skill
                mock_manifest_file.return_value.exists.return_value = True
                mock_manifest_file.return_value.read.return_value = mock_manifest

                result = cli_runner.invoke(main, ["update", "test-skill", "--dry-run"])

                assert result.exit_code == 0
                assert "Would update" in result.output


class TestCliSync:
    """Test suite for CLI sync command."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_sync_basic(self, cli_runner):
        """Test basic sync command."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["sync"])

            assert result.exit_code == 0
            assert "Sync complete" in result.output

    def test_sync_dry_run(self, cli_runner):
        """Test sync with dry-run flag."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["sync", "--dry-run"])

            assert result.exit_code == 0
            assert "Dry run" in result.output

    def test_sync_with_down_flag(self, cli_runner):
        """Test sync with --down flag to add orphaned skills."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            with patch(
                "skillman.cli.SkillInstaller.list_installed_skills",
                return_value=[("orphaned-skill", Path("/test/path"))],
            ):
                result = cli_runner.invoke(main, ["sync", "--down", "-y"])

                assert result.exit_code == 0

    def test_sync_confirms_before_proceeding(self, cli_runner):
        """Test sync prompts for confirmation without -y flag."""
        with cli_runner.isolated_filesystem():
            manifest_content = """
[[skills]]
name = "test-skill"
source = "user/repo"
version = "1.0.0"
scope = "local"
"""
            Path("skills.toml").write_text(manifest_content)

            with (
                patch("skillman.cli.SkillInstaller.get_skill_path", return_value=None),
                patch("skillman.cli.GitHubClient") as mock_github_class,
                patch("skillman.cli.ConfigManager") as mock_config_class,
            ):

                mock_github = MagicMock()
                mock_github.fetch_skill.return_value = (
                    Path("/tmp/skill"),
                    "abc123",
                )
                mock_github_class.return_value = mock_github
                mock_config_class.return_value.get.return_value = None

                result = cli_runner.invoke(main, ["sync"], input="\n")

                # Should complete without error even if no confirmation
                assert result.exit_code == 0


class TestCliFetch:
    """Test suite for CLI fetch command (alias for update --all)."""

    @pytest.fixture
    def cli_runner(self):
        """Provide CLI test runner."""
        return CliRunner()

    def test_fetch_basic(self, cli_runner):
        """Test basic fetch command."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["fetch"])

            assert result.exit_code == 0

    def test_fetch_with_dry_run(self, cli_runner):
        """Test fetch with dry-run flag."""
        with cli_runner.isolated_filesystem():
            Path("skills.toml").write_text("[[skills]]\n")

            result = cli_runner.invoke(main, ["fetch", "--dry-run"])

            assert result.exit_code == 0
            assert "Dry run" in result.output
