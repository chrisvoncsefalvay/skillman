"""CLI interface for skillman."""

import sys
import tempfile
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from skillman.config import ConfigManager
from skillman.claude_marketplace import ClaudeMarketplaceManager
from skillman.github import SkillSpec, GitHubClient, SkillValidator
from skillman.installer import SkillInstaller
from skillman.models import Skill
from skillman.utils import LockFileManager, ManifestFile


# Console for output
console = Console(force_terminal=True, legacy_windows=False)


@click.group()
@click.version_option()
def main():
    """Skillman: CLI tool for managing Claude skills."""
    pass


@main.command()
def init():
    """Create empty skills.toml in current directory."""
    manifest_file = ManifestFile(Path("skills.toml"))

    if manifest_file.exists():
        console.print("[yellow]skills.toml already exists[/yellow]")
        return

    try:
        manifest_file.create_empty()
        console.print("[green]Created skills.toml[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("skill_spec")
@click.option(
    "-s",
    "--scope",
    type=click.Choice(["local", "user"]),
    default="local",
    help="Installation scope (default: local)",
)
@click.option("--no-verify", is_flag=True, help="Skip skill validation")
@click.option("--force", is_flag=True, help="Overwrite existing skill")
@click.option(
    "--dangerously-skip-permissions",
    is_flag=True,
    help="Skip permission warnings (not recommended)",
)
def add(
    skill_spec: str,
    scope: str,
    no_verify: bool,
    force: bool,
    dangerously_skip_permissions: bool,
):
    """Add and install a skill from GitHub."""
    try:
        # Parse skill specification
        try:
            parsed_spec = SkillSpec(skill_spec)
        except ValueError as e:
            console.print(f"[red]Invalid skill specification: {e}[/red]")
            sys.exit(1)

        # Show security warning unless skipped
        if not dangerously_skip_permissions:
            console.print(
                "[yellow]Security warning: Skills can execute code and access system resources.[/yellow]"
            )
            console.print()
            console.print("Before installing a skill, please consider:")
            console.print("  - Install only from trusted sources")
            console.print("  - Review what the skill does before use")
            console.print("  - Skills can read, create, or modify files")
            console.print("  - Skills can execute system commands")
            console.print()
            console.print(
                "For more information on skill security and permissions, see:"
            )
            console.print(
                "  https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_2746475e70"
            )
            console.print()

            if not click.confirm("Do you want to continue installing this skill?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Get GitHub token if available
        config = ConfigManager()
        github_token = config.get("github-token")

        # Fetch skill from GitHub
        console.print(f"[cyan]Fetching {skill_spec}...[/cyan]")
        github_client = GitHubClient(github_token)

        with tempfile.TemporaryDirectory(prefix="skillman_add_") as temp_dir:
            skill_path, resolved_sha = github_client.fetch_skill(
                parsed_spec, Path(temp_dir)
            )

            # Validate skill
            if not no_verify:
                console.print("[cyan]Validating skill...[/cyan]")
                result = SkillValidator.validate(skill_path)
                if not result.is_valid:
                    console.print(
                        f"[red]Validation failed: {result.error_message}[/red]"
                    )
                    sys.exit(1)

            # Install skill
            console.print(f"[cyan]Installing to {scope} scope...[/cyan]")
            success, message = SkillInstaller.install_skill(
                skill_path, parsed_spec.repo, scope, force
            )
            if not success:
                console.print(f"[red]{message}[/red]")
                sys.exit(1)

            console.print(f"[green]{message}[/green]")

            # Get installed skill path for marketplace registration
            installed_skill_path = SkillInstaller.get_skill_path(
                parsed_spec.repo, scope
            )

            # Update manifest
            manifest_file = ManifestFile(Path("skills.toml"))
            manifest = manifest_file.read_or_create()

            skill = Skill(
                name=parsed_spec.repo,
                source=str(parsed_spec),
                version=parsed_spec.version,
                scope=scope,
            )

            # Remove existing if force
            if force:
                manifest.remove_skill(skill.name)

            if not manifest.has_skill(skill.name):
                manifest.add_skill(skill)
                manifest_file.write(manifest)

                # Update lock file
                lock_manager = LockFileManager(Path("skills.lock"))
                lock_file = lock_manager.read_or_create()
                lock_file.set_entry(
                    skill.name,
                    str(parsed_spec),
                    parsed_spec.version,
                    resolved_sha,
                    parsed_spec.version,
                )
                lock_manager.write(lock_file)

                console.print("[green]Added to skills.toml[/green]")

                # Register skill with Claude marketplace
                if installed_skill_path:
                    console.print(
                        f"[cyan]Registering {skill.name} with Claude marketplace...[/cyan]"
                    )
                    success, marketplace_message = (
                        ClaudeMarketplaceManager.add_skill_to_marketplace(
                            installed_skill_path, skill.name
                        )
                    )
                    if success:
                        console.print(f"[green]{marketplace_message}[/green]")
                    else:
                        console.print(f"[yellow]{marketplace_message}[/yellow]")
            else:
                console.print("[yellow]Skill already in manifest[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("skillname")
@click.option(
    "-s",
    "--scope",
    type=click.Choice(["local", "user"]),
    default=None,
    help="Installation scope",
)
@click.option("--keep-files", is_flag=True, help="Keep installed files")
def remove(skillname: str, scope: Optional[str], keep_files: bool):
    """Remove skill from manifest and optionally filesystem."""
    try:
        manifest_file = ManifestFile(Path("skills.toml"))
        if not manifest_file.exists():
            console.print("[yellow]No skills.toml found[/yellow]")
            return

        manifest = manifest_file.read()

        # Remove from manifest
        if manifest.remove_skill(skillname):
            manifest_file.write(manifest)
            console.print(f"[green]Removed {skillname} from manifest[/green]")

            # Remove lock entry
            lock_manager = LockFileManager(Path("skills.lock"))
            lock_file = lock_manager.read_or_create()
            if skillname in lock_file.entries:
                del lock_file.entries[skillname]
                lock_manager.write(lock_file)
        else:
            console.print(f"[yellow]{skillname} not found in manifest[/yellow]")

        # Remove from filesystem if not --keep-files
        if not keep_files:
            scopes = [scope] if scope else ["local", "user"]
            for s in scopes:
                success, message = SkillInstaller.uninstall_skill(skillname, s)
                if success:
                    console.print(f"[green]{message}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("skill_spec")
@click.option("--no-verify", is_flag=True, help="Skip validation")
def verify(skill_spec: str, no_verify: bool):
    """Check if skill exists and has valid structure."""
    try:
        # Parse specification
        try:
            parsed_spec = SkillSpec(skill_spec)
        except ValueError as e:
            console.print(f"[red]Invalid specification: {e}[/red]")
            sys.exit(1)

        # Get GitHub token
        config = ConfigManager()
        github_token = config.get("github-token")

        # Fetch skill
        console.print(f"[cyan]Verifying {skill_spec}...[/cyan]")
        github_client = GitHubClient(github_token)

        with tempfile.TemporaryDirectory(prefix="skillman_verify_") as temp_dir:
            skill_path, resolved_sha = github_client.fetch_skill(
                parsed_spec, Path(temp_dir)
            )

            # Validate
            result = SkillValidator.validate(skill_path)

            if result.is_valid:
                console.print("[green]Valid skill[/green]")
                console.print(f"  Repository: {parsed_spec.repo_url}")
                console.print(f"  Path: {parsed_spec.skill_path}")
                console.print(f"  Resolved SHA: {resolved_sha}")

                if result.metadata:
                    if result.metadata.title:
                        console.print(f"  Title: {result.metadata.title}")
                    if result.metadata.description:
                        console.print(f"  Description: {result.metadata.description}")
                    if result.metadata.license:
                        console.print(f"  License: {result.metadata.license}")
                    if result.metadata.author:
                        console.print(f"  Author: {result.metadata.author}")
                    if result.metadata.version:
                        console.print(f"  Version: {result.metadata.version}")
                    if result.metadata.tags:
                        console.print(f"  Tags: {', '.join(result.metadata.tags)}")
            else:
                console.print(f"[red]Invalid: {result.error_message}[/red]")
                sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command(name="list")
@click.option(
    "-s",
    "--scope",
    type=click.Choice(["local", "user"]),
    default=None,
    help="Show only specified scope",
)
def cmd_list(scope: Optional[str]):
    """List installed skills with status."""
    try:
        manifest_file = ManifestFile(Path("skills.toml"))
        manifest = manifest_file.read_or_create()

        # Create table
        table = Table(title="Installed Skills")
        table.add_column("Name")
        table.add_column("Version (Manifest)")
        table.add_column("Version (Installed)")
        table.add_column("Scope")
        table.add_column("Status")

        # Get installed skills
        installed = {
            name: path for name, path in SkillInstaller.list_installed_skills(scope)
        }

        # Add manifest skills
        shown = set()
        for skill in manifest.skills:
            if scope and skill.scope != scope:
                continue

            shown.add(skill.name)
            installed_version = "N/A"
            status = "missing"

            if skill.name in installed:
                status = "synced"
                # Try to get version from lock file
                lock_manager = LockFileManager(Path("skills.lock"))
                lock_file = lock_manager.read_or_create()
                if skill.name in lock_file.entries:
                    installed_version = lock_file.entries[skill.name].resolved_version

            table.add_row(
                skill.name, skill.version, installed_version, skill.scope, status
            )

        # Add orphaned skills
        for name in installed:
            if name not in shown:
                table.add_row(name, "N/A", "installed", "?", "orphaned")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("skillname")
def show(skillname: str):
    """Display detailed skill information."""
    try:
        # Check manifest
        manifest_file = ManifestFile(Path("skills.toml"))
        manifest = manifest_file.read_or_create()
        manifest_skill = manifest.get_skill(skillname)

        # Check installed
        installed_path = SkillInstaller.get_skill_path(skillname)

        if not manifest_skill and not installed_path:
            console.print(f"[yellow]Skill '{skillname}' not found[/yellow]")
            return

        console.print(f"[bold]{skillname}[/bold]")

        if manifest_skill:
            console.print(f"  Source: {manifest_skill.source}")
            console.print(f"  Version (manifest): {manifest_skill.version}")
            console.print(f"  Scope: {manifest_skill.scope}")
            if manifest_skill.aliases:
                console.print(f"  Aliases: {', '.join(manifest_skill.aliases)}")

        if installed_path:
            console.print(f"  Installed path: {installed_path}")

            # Validate to extract metadata
            result = SkillValidator.validate(installed_path)
            if result.is_valid and result.metadata:
                if result.metadata.title:
                    console.print(f"  Title: {result.metadata.title}")
                if result.metadata.description:
                    console.print(f"  Description: {result.metadata.description}")
                if result.metadata.license:
                    console.print(f"  License: {result.metadata.license}")
                if result.metadata.author:
                    console.print(f"  Author: {result.metadata.author}")
                if result.metadata.version:
                    console.print(f"  Skill version: {result.metadata.version}")
                if result.metadata.tags:
                    console.print(f"  Tags: {', '.join(result.metadata.tags)}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("skillname", required=False)
@click.option("--all", is_flag=True, help="Update all skills")
@click.option("--dry-run", is_flag=True, help="Show what would happen")
def update(skillname: Optional[str], all: bool, dry_run: bool):
    """Update installed skills to manifest versions."""
    try:
        manifest_file = ManifestFile(Path("skills.toml"))
        if not manifest_file.exists():
            console.print("[yellow]No skills.toml found[/yellow]")
            return

        manifest = manifest_file.read()

        skills_to_update = []
        if all:
            skills_to_update = manifest.skills
        elif skillname:
            skill = manifest.get_skill(skillname)
            if not skill:
                console.print(f"[yellow]{skillname} not found in manifest[/yellow]")
                return
            skills_to_update = [skill]
        else:
            console.print("[yellow]Specify skill name or use --all[/yellow]")
            return

        if dry_run:
            console.print("[cyan]Dry run - no changes will be made[/cyan]")

        for skill in skills_to_update:
            console.print(
                f"[cyan]Would update {skill.name} to {skill.version}[/cyan]"
                if dry_run
                else f"[cyan]Updating {skill.name}...[/cyan]"
            )

            if not dry_run:
                # Fetch and install
                config = ConfigManager()
                github_token = config.get("github-token")
                github_client = GitHubClient(github_token)

                parsed_spec = SkillSpec(skill.source)
                with tempfile.TemporaryDirectory(prefix="skillman_update_") as temp_dir:
                    skill_path, resolved_sha = github_client.fetch_skill(
                        parsed_spec, Path(temp_dir)
                    )
                    success, message = SkillInstaller.install_skill(
                        skill_path, skill.name, skill.scope, force=True
                    )

                    if success:
                        # Update lock file
                        lock_manager = LockFileManager(Path("skills.lock"))
                        lock_file = lock_manager.read_or_create()
                        lock_file.set_entry(
                            skill.name,
                            skill.source,
                            skill.version,
                            resolved_sha,
                            skill.version,
                        )
                        lock_manager.write(lock_file)
                        console.print(f"[green]Updated {skill.name}[/green]")

                        # Register skill with Claude marketplace
                        installed_skill_path = SkillInstaller.get_skill_path(
                            skill.name, skill.scope
                        )
                        if installed_skill_path:
                            success, marketplace_message = (
                                ClaudeMarketplaceManager.add_skill_to_marketplace(
                                    installed_skill_path, skill.name
                                )
                            )
                            if not success:
                                console.print(f"[yellow]{marketplace_message}[/yellow]")
                    else:
                        console.print(
                            f"[red]Failed to update {skill.name}: {message}[/red]"
                        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--dry-run", is_flag=True, help="Show what would happen")
@click.option("-y", "--yes", is_flag=True, help="Don't prompt for confirmation")
def fetch(dry_run: bool, yes: bool):
    """Fetch and update all skills (alias for update --all)."""
    ctx = click.get_current_context()
    ctx.invoke(update, skillname=None, all=True, dry_run=dry_run)


@main.command()
@click.option("--up", is_flag=True, help="Update skills to latest matching constraints")
@click.option(
    "--down", is_flag=True, help="Add installed-but-unlisted skills to manifest"
)
@click.option("-y", "--yes", is_flag=True, help="Don't prompt for confirmation")
@click.option("--dry-run", is_flag=True, help="Show what would happen")
def sync(up: bool, down: bool, yes: bool, dry_run: bool):
    """Synchronise skills between manifest and installed."""
    try:
        manifest_file = ManifestFile(Path("skills.toml"))
        manifest = manifest_file.read_or_create()
        lock_manager = LockFileManager(Path("skills.lock"))
        lock_file = lock_manager.read_or_create()

        if dry_run:
            console.print("[cyan]Dry run - no changes will be made[/cyan]")

        # Install/update from manifest
        console.print("[cyan]Syncing from manifest...[/cyan]")
        for skill in manifest.skills:
            installed_path = SkillInstaller.get_skill_path(skill.name, skill.scope)
            if not installed_path:
                console.print(
                    f"[cyan]Would install {skill.name}[/cyan]"
                    if dry_run
                    else f"[cyan]Installing {skill.name}...[/cyan]"
                )

                if not dry_run:
                    config = ConfigManager()
                    github_token = config.get("github-token")
                    github_client = GitHubClient(github_token)

                    parsed_spec = SkillSpec(skill.source)
                    with tempfile.TemporaryDirectory(
                        prefix="skillman_sync_"
                    ) as temp_dir:
                        skill_path, resolved_sha = github_client.fetch_skill(
                            parsed_spec, Path(temp_dir)
                        )
                        success, message = SkillInstaller.install_skill(
                            skill_path, skill.name, skill.scope
                        )
                        if success:
                            console.print(f"[green]Installed {skill.name}[/green]")
                            lock_file.set_entry(
                                skill.name,
                                skill.source,
                                skill.version,
                                resolved_sha,
                                skill.version,
                            )

                            # Register skill with Claude marketplace
                            installed_skill_path = SkillInstaller.get_skill_path(
                                skill.name, skill.scope
                            )
                            if installed_skill_path:
                                success, marketplace_message = (
                                    ClaudeMarketplaceManager.add_skill_to_marketplace(
                                        installed_skill_path, skill.name
                                    )
                                )
                                if not success:
                                    console.print(
                                        f"[yellow]{marketplace_message}[/yellow]"
                                    )
                        else:
                            console.print(f"[red]Failed: {message}[/red]")

        if down:
            # Add orphaned skills to manifest
            console.print("[cyan]Checking for orphaned skills...[/cyan]")
            installed = SkillInstaller.list_installed_skills()
            for name, path in installed:
                if not manifest.has_skill(name):
                    console.print(
                        f"[cyan]Would add {name} to manifest[/cyan]"
                        if dry_run
                        else f"[cyan]Adding {name} to manifest...[/cyan]"
                    )

                    if not dry_run:
                        skill = Skill(name=name, source="unknown", scope="local")
                        manifest.add_skill(skill)
                        manifest_file.write(manifest)

        if not dry_run and not up and not down:
            lock_manager.write(lock_file)

        console.print("[green]Sync complete[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "-s",
    "--scope",
    type=click.Choice(["local", "user"]),
    default=None,
    help="Clean only specified scope",
)
@click.option("--dry-run", is_flag=True, help="Show what would happen")
@click.option("-y", "--yes", is_flag=True, help="Don't prompt for confirmation")
def clean(scope: Optional[str], dry_run: bool, yes: bool):
    """Remove orphaned skills (installed but not in manifest)."""
    try:
        manifest_file = ManifestFile(Path("skills.toml"))
        manifest = manifest_file.read_or_create()

        installed = SkillInstaller.list_installed_skills(scope)
        orphaned = [name for name, _ in installed if not manifest.has_skill(name)]

        if not orphaned:
            console.print("[green]No orphaned skills found[/green]")
            return

        console.print("[cyan]Orphaned skills:[/cyan]")
        for name in orphaned:
            console.print(f"  - {name}")

        if dry_run:
            console.print("[cyan]Dry run - no changes will be made[/cyan]")
            return

        if not yes:
            if not click.confirm("Remove these skills?"):
                return

        for name in orphaned:
            success, message = SkillInstaller.uninstall_skill(name, scope or "local")
            if success:
                console.print(f"[green]Removed {name}[/green]")
            else:
                console.print(f"[red]Failed to remove {name}: {message}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.group()
def config():
    """Manage configuration."""
    pass


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def set_config(key: str, value: str):
    """Set configuration value."""
    try:
        config_manager = ConfigManager()
        config_manager.set(key, value)
        console.print(f"[green]Set {key} = {value}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@config.command(name="get")
@click.argument("key")
def get_config(key: str):
    """Get configuration value."""
    try:
        config_manager = ConfigManager()
        value = config_manager.get(key)
        if value is not None:
            console.print(f"{key} = {value}")
        else:
            console.print(f"[yellow]{key} not set[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@config.command(name="list")
def list_config():
    """List all configuration values."""
    try:
        config_manager = ConfigManager()
        all_config = config_manager.list_all()

        if not all_config:
            console.print("[yellow]No configuration set[/yellow]")
            return

        for key, value in all_config.items():
            console.print(f"{key} = {value}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
