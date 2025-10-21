# skillman: a CLI for managing Claude skills


[![Tests and Build](https://github.com/chrisvoncsefalvay/skillman/workflows/Tests%20and%20Build/badge.svg)](https://github.com/chrisvoncsefalvay/skillman/actions/workflows/tests.yml)
[![Code Quality](https://github.com/chrisvoncsefalvay/skillman/workflows/Code%20Quality%20Checks/badge.svg)](https://github.com/chrisvoncsefalvay/skillman/actions/workflows/quality.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-skillman-orange)](https://pypi.org/project/skillman/)



A Python CLI for managing Claude skills from GitHub repositories. Handles installation, versioning, and synchronisation of skills across user and project scopes -- mostly gracefully.

## Installation

### Via pip (from PyPI)

Once published to PyPI:

```bash
pip install skillman
```

### Via uv (recommended)

The uv tool is a fast, all-in-one Python package installer and tool runner:

```bash
uv tool install skillman
```

Or run directly without installing:

```bash
uv run --with skillman skillman init
```

[Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Via pipx

```bash
pipx install skillman
```

### From source (development)

Clone the repository and install in development mode:

```bash
git clone https://github.com/chrisvoncsefalvay/skillman.git
cd skillman
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick start

Create an empty manifest in your project:

```bash
skillman init
```

List installed skills:

```bash
skillman list
```

## Commands

### skillman init

Create empty skills.toml in current directory.

### skillman add <skill-spec> [options]

Add and install a skill from GitHub.

By default, the tool displays a security warning before installation to help you make informed decisions about which skills to install.

Options:
- `-s, --scope <local|user>`: Installation scope (default: local)
- `--no-verify`: Skip skill validation
- `--force`: Overwrite existing skill
- `--dangerously-skip-permissions`: Skip security warning (not recommended)

Skill specification format:
- Single skill repo: `username/reponame[@version]`
- Skill in repository folder: `username/reponame/foldername[@version]`
- Nested skill (multi-tier): `username/reponame/folder1/folder2/...[@version]`
- Version: `@1.2.3` (tag), `@abc1234` (SHA), `@latest` or omitted (latest)

Supports arbitrary nesting levels. The tool will look for SKILL.md in the specified path.

Example:

```bash
skillman add anthropics/skills/canvas-design
skillman add anthropics/skills/document-skills/docx
skillman add myorg/repo/custom-skill@1.2.3
```

### skillman remove <skillname> [options]

Remove skill from manifest and filesystem.

Options:
- `-s, --scope <local|user>`: Only remove from specified scope
- `--keep-files`: Remove only from manifest, keep installed files

### skillman verify <skill-spec>

Check if skill exists at source and has valid structure.

### skillman list [options]

List installed skills with status.

Options:
- `-s, --scope <local|user>`: Show only specified scope

Status values:
- synced: Installed and matches manifest version
- outdated: Installed version differs from manifest
- orphaned: Installed but not in manifest
- missing: In manifest but not installed

### skillman show <skillname>

Display detailed skill information.

### skillman update [<skillname>|--all] [--dry-run]

Update installed skills to versions specified in manifest.

Options:
- `--all`: Update all skills
- `--dry-run`: Show what would happen

Examples:

```bash
skillman update canvas-design
skillman update --all
skillman update --dry-run
```

### skillman fetch [--dry-run]

Fetch and update all skills (alias for update --all).

### skillman sync [options]

Synchronise skills between manifest and installed.

Options:
- `--up`: Update skills to latest matching manifest constraints
- `--down`: Add installed-but-unlisted skills to manifest
- `-y, --yes`: Don't prompt for confirmation
- `--dry-run`: Show what would happen

### skillman clean [options]

Remove orphaned skills (installed but not in manifest).

Options:
- `-s, --scope <local|user>`: Clean only specified scope
- `--dry-run`: Show what would happen
- `-y, --yes`: Don't prompt for confirmation

### skillman config <command> [args]

Manage configuration.

Subcommands:
- `get <key>`: Get configuration value
- `set <key> <value>`: Set configuration value
- `list`: List all configuration values

Configuration keys:
- `default-scope`: Default installation scope (local or user)
- `github-token`: GitHub token for private repositories

Configuration file location: `~/.skillman/config.toml`

Example:

```bash
skillman config set github-token your-token-here
skillman config get default-scope
skillman config list
```

## Installation paths

Skills are installed to:
- User scope: `~/.claude/skills/user/`
- Project scope: `./.claude/skills/`

## Manifest file

Skills are declared in `skills.toml`:

```toml
[tool.skillman]
version = "1.0.0"

[[skills]]
name = "canvas"
source = "anthropics/skills/canvas-design"
version = "latest"
scope = "user"
aliases = ["design"]

[[skills]]
name = "custom"
source = "myorg/repo/custom-skill"
version = "1.0.0"
scope = "local"
```

## Security considerations

Skills can execute code and access system resources. Before installing a skill, you should:

1. **Install only from trusted sources**: Only install skills from repositories you trust or that have been recommended by reliable sources.

2. **Review skill functionality**: Use `skillman verify` to examine what a skill does before installing it.

3. **Understand permissions**: Skills can:
   - Read, create, and modify files on your system
   - Execute system commands
   - Access and manipulate data

4. **Permission warnings**: By default, skillman displays a security warning and asks for confirmation before installing any skill. This helps you make informed decisions.

5. **Skipping warnings**: The `--dangerously-skip-permissions` flag allows skipping the security warning. This is not recommended except for trusted, well-known skills.

For detailed information about skill security and permissions, see:
[Using Skills in Claude - Security](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_2746475e70)

## Skill metadata extraction

Skillman automatically extracts metadata from SKILL.md front matter in YAML format:

```yaml
---
title: My Skill
description: What this skill does
license: MIT
author: Author Name
version: 1.0.0
tags:
  - documentation
  - productivity
---

# Skill content...
```

Extracted metadata is displayed when:

- Verifying a skill: `skillman verify username/repo/skill`
- Showing skill details: `skillman show skillname`

If no YAML front matter is present, the first non-header paragraph from the markdown is used as the description.

## Lock file

`skills.lock` is automatically generated and maintains exact commit SHAs for reproducible installations. This file should be committed to version control.

## Configuration

Create `~/.skillman/config.toml` for global configuration:

```toml
default-scope = "local"
github-token = "your-github-token"
```

Or use the `skillman config` command:

```bash
skillman config set github-token your-token
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black skillman
```

Type check:

```bash
mypy skillman
```

## Requirements

- Python 3.8+
- click: CLI framework
- rich: Formatted output
- GitPython: Git operations
- tomli/tomli_w: TOML parsing
- requests: HTTP operations

## Architecture

The tool is structured as follows:

- `cli.py`: Click-based CLI commands
- `models.py`: Data models (Skill, Manifest, LockFile)
- `config.py`: Configuration management
- `github.py`: GitHub operations and skill validation
- `installer.py`: Skill installation and management
- `utils.py`: Utility functions for manifest and lock file handling

All output uses the Rich library for ASCII-compatible formatting (no Unicode box-drawing or emoji).

## Error handling

The tool provides (mostly) clear error messages for:
- Network failures (with retry suggestions)
- Validation failures (showing what's wrong with the skill structure)
- Conflict warnings (these are only warnings as Claude should determine how to actually resolve them)
- Sync failures (showing which skills succeeded and which failed)

## License

MIT

Made with ❤️ in the Mile High City 🏔️ by [Chris von Csefalvay](https://chrisvoncsefalvay.com) and 🐶 Oliver.
