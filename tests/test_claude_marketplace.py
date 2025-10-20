"""Tests for Claude marketplace integration."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from skillman.claude_marketplace import ClaudeMarketplaceManager


class TestClaudeMarketplaceManager:
    """Test suite for ClaudeMarketplaceManager."""

    def test_add_skill_to_marketplace_success(self):
        """Test successful skill addition to marketplace."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Skill registered successfully"
        mock_result.stderr = ""

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is True
        assert "Successfully added test-skill to Claude marketplace" in message

    def test_add_skill_to_marketplace_failure(self):
        """Test failed skill addition to marketplace."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Skill already exists"

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is False
        assert "Failed to add test-skill to marketplace" in message
        assert "Skill already exists" in message

    def test_add_skill_to_marketplace_timeout(self):
        """Test timeout when adding skill to marketplace."""
        with patch(
            "skillman.claude_marketplace.subprocess.run",
            side_effect=subprocess.TimeoutExpired(["cmd"], 120),
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is False
        assert "Timeout when adding test-skill to Claude marketplace" in message

    def test_add_skill_to_marketplace_exception(self):
        """Test exception handling when adding skill to marketplace."""
        with patch(
            "skillman.claude_marketplace.subprocess.run",
            side_effect=RuntimeError("Test error"),
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is False
        assert "Error adding test-skill to marketplace" in message
        assert "Test error" in message

    def test_add_skill_subprocess_command(self):
        """Test that subprocess is called with correct parameters."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ) as mock_run:
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            ClaudeMarketplaceManager.add_skill_to_marketplace(skill_path, skill_name)

            # Verify subprocess was called with correct arguments
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            cmd = call_args[0][0]

            # Check that the command includes the expected components
            assert "-m" in cmd
            assert "claude" in cmd
            assert "headless" in cmd
            assert "--dangerously-skip-permissions" in cmd
            assert "plugin" in cmd
            assert "marketplace" in cmd
            assert "add" in cmd
            assert str(skill_path) in cmd

    def test_add_skill_subprocess_timeout_parameter(self):
        """Test that subprocess is called with timeout parameter."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ) as mock_run:
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            ClaudeMarketplaceManager.add_skill_to_marketplace(skill_path, skill_name)

            # Verify timeout is set to 120 seconds
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["timeout"] == 120

    def test_add_skill_subprocess_capture_output(self):
        """Test that subprocess captures stdout and stderr."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ) as mock_run:
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            ClaudeMarketplaceManager.add_skill_to_marketplace(skill_path, skill_name)

            # Verify capture_output and text parameters
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["capture_output"] is True
            assert call_kwargs["text"] is True

    def test_add_skill_uses_stderr_on_failure(self):
        """Test that error message uses stderr when available."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Permission denied"

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is False
        assert "Permission denied" in message

    def test_add_skill_uses_stdout_on_failure_if_no_stderr(self):
        """Test that error message uses stdout when stderr is empty."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Error message"
        mock_result.stderr = ""

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ):
            skill_path = Path("/test/skill/path")
            skill_name = "test-skill"

            success, message = ClaudeMarketplaceManager.add_skill_to_marketplace(
                skill_path, skill_name
            )

        assert success is False
        assert "Error message" in message

    def test_add_skill_various_path_types(self):
        """Test with various path types."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        test_paths = [
            Path("/home/user/.claude/skills/my-skill"),
            Path("./claude/skills/local-skill"),
            Path("C:\\Users\\User\\.claude\\skills\\windows-skill"),
        ]

        with patch(
            "skillman.claude_marketplace.subprocess.run", return_value=mock_result
        ) as mock_run:
            for test_path in test_paths:
                ClaudeMarketplaceManager.add_skill_to_marketplace(
                    test_path, "test-skill"
                )

            # Verify subprocess was called for each path
            assert mock_run.call_count == len(test_paths)
