# Product Requirements Document: SkillMeat

**Version:** 1.0
**Date:** 2025-11-05
**Status:** Draft - MVP Definition
**Owner:** Product Team

---

## Executive Summary

**SkillMeat** is a personal collection manager for Claude Code configurations, enabling developers to maintain, version, and deploy Claude artifacts (Skills, Commands, Agents, MCP servers, Hooks) across multiple projects. Unlike public catalogs, SkillMeat focuses on personal productivity through intelligent collection management, upstream tracking, and flexible deployment strategies.

### Vision Statement

> "Every developer's personal library of Claude configurations, intelligently managed and effortlessly deployed across all their projects."

### Success Metrics (6 Months Post-MVP)

- **Adoption**: 1,000+ active users managing personal collections
- **Engagement**: Average 20+ artifacts per collection
- **Retention**: 60%+ weekly active users
- **Satisfaction**: 4.5+ star rating, <5% critical bug rate

---

## 1. Problem Statement

### Current Pain Points

1. **Fragmentation**: Developers copy/paste Claude configurations between projects manually
2. **No Collections**: Can't maintain curated sets of related artifacts
3. **Update Hell**: No way to track upstream changes or merge local modifications
4. **Discovery Gap**: Can't find previously created configurations across projects
5. **Tool Sprawl**: Need separate tools for Skills (skillman), Commands (claude-cmd), MCP servers (mcpm)

### User Personas

#### Primary: Solo Developer (Power User)
- **Name**: Alex the Fullstack Developer
- **Context**: Works on 5-10 active projects simultaneously
- **Pain**: Spends 30min/week copying configurations between projects
- **Goal**: Personal productivity system that works everywhere
- **Quote**: _"I keep forgetting which project has my best code review command"_

#### Secondary: Small Team Lead
- **Name**: Jordan the Tech Lead
- **Context**: Manages team of 3-5 developers across multiple repos
- **Pain**: Team members have inconsistent Claude setups
- **Goal**: Recommend standards without forcing adoption
- **Quote**: _"I want to share our best practices but let people customize"_

---

## 2. Product Overview

### Core Concept: Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│  Collection (Personal Library)          │  ← Master repository
│  ~/.skillmeat/collection/               │
│  - Curated artifacts                    │
│  - Upstream tracking                    │
│  - Version history                      │
└─────────────────────────────────────────┘
             │
             ├── deploy ──→  Project A (.claude/)
             ├── deploy ──→  Project B (.claude/)
             └── deploy ──→  Project C (.claude/)
                   │
                   └── Can fork & customize locally
```

### Key Differentiators

| Feature | SkillMeat | Existing Tools |
|---------|-----------|----------------|
| **Unified Management** | Skills + Commands + Agents + MCP + Hooks | Separate tools per type |
| **Collection-First** | Named collections, inheritance | Individual items only |
| **Smart Updates** | Fork tracking, merge strategies, conflict resolution | Replace or manual merge |
| **Cross-Project** | Global search, usage analytics | Per-project only |
| **Interfaces** | CLI + Web UI | CLI only or Web only |
| **Personal Focus** | Optimize for individual, optional team sharing | Public catalogs or team-only |

---

## 3. MVP Scope

### 3.1 In-Scope Features

#### Phase 1: Core Collection Management (MVP)

**F1.1: Collection Initialization**
- Create personal collection directory structure
- Initialize collection manifest (collection.toml)
- Support multiple named collections
- **User Story**: _"As a developer, I want to create a new collection so I can organize my Claude configurations"_

**F1.2: Artifact Addition to Collection**
- Add from GitHub repo (username/repo/path@version)
- Add from local project (.claude/ directories)
- Add from local filesystem (custom locations)
- Support artifact types: Skills, Commands, Agents
- Extract metadata automatically
- **User Story**: _"As a developer, I want to add my best code review command to my collection so I can reuse it in other projects"_

**F1.3: Collection Viewing**
- List all artifacts in collection
- Show detailed artifact information
- Display upstream tracking status (synced/outdated/modified)
- Filter by type, tags, usage
- **User Story**: _"As a developer, I want to see what's in my collection so I can remember what tools I have"_

**F1.4: Project Deployment**
- Deploy selected artifacts from collection to project
- Deploy entire collection to project
- Interactive selection mode
- Respect existing project configurations
- **User Story**: _"As a developer, I want to deploy my web-dev collection to a new Next.js project so I can start working immediately"_

**F1.5: Upstream Tracking**
- Track original source URL for each artifact
- Check for upstream updates
- Display diff between local and upstream
- **User Story**: _"As a developer, I want to know when upstream skills are updated so I can benefit from improvements"_

**F1.6: Basic Versioning**
- Snapshot collection before changes
- List version history
- Rollback to previous snapshot
- **User Story**: _"As a developer, I want to undo changes to my collection if something breaks"_

#### Phase 2: Intelligence & Sync (Post-MVP)

**F2.1: Cross-Project Search**
- Search artifacts across all projects
- Find similar/duplicate artifacts
- Tag-based search
- **User Story**: _"As a developer, I want to find where I used that security scanning agent before"_

**F2.2: Usage Analytics**
- Track artifact usage across projects
- Identify most/least used artifacts
- Suggest cleanup opportunities
- **User Story**: _"As a developer, I want to know which commands I actually use so I can clean up clutter"_

**F2.3: Smart Updates**
- Merge upstream changes with local modifications
- Conflict detection and resolution UI
- Update strategies (take upstream, keep local, manual merge)
- **User Story**: _"As a developer, I want to update from upstream without losing my customizations"_

**F2.4: Collection Sync**
- Sync collection changes back from projects
- Detect project-level improvements
- Promote project customizations to collection
- **User Story**: _"As a developer, I made improvements in my project and want to add them to my collection"_

#### Phase 3: Advanced Features (Future)

**F3.1: Web Interface**
- Browse collections visually
- Edit artifacts with preview
- Deploy via web UI
- Dashboard with analytics

**F3.2: Team Sharing**
- Export collection for sharing
- Import shared collections
- Recommend to team without requiring
- Per-project override of collection defaults

**F3.3: MCP Server Management**
- Add MCP servers to collection
- Deploy with environment configuration
- Manage mcpServers in settings.json

**F3.4: Marketplace Integration**
- Browse public Claude marketplaces
- Install to collection from marketplace
- Publish collection to marketplace (optional)

### 3.2 Out-of-Scope (MVP)

- ❌ Cloud sync between machines (use Git)
- ❌ Public catalog/marketplace (personal focus)
- ❌ Collaborative editing (single user)
- ❌ Mobile interface
- ❌ Plugin system for extensibility
- ❌ AI-powered artifact generation
- ❌ Integration testing of deployed artifacts
- ❌ Performance analytics of Claude usage

---

## 4. User Experience

### 4.1 CLI Interaction Model

**Design Principles:**
1. **Fast**: Common operations in 1-2 commands
2. **Safe**: Confirm destructive operations, provide undo
3. **Discoverable**: Help text, examples, suggestions
4. **Consistent**: Follow Git-like patterns (init, add, commit, push metaphor)

**Command Structure:**
```bash
skillmeat <command> [subcommand] [arguments] [options]
```

### 4.2 Core Workflows

#### Workflow 1: Initialize New Collection
```bash
# Create default collection
skillmeat init

# Create named collection
skillmeat collection create web-dev
```

**Expected Output:**
```
✓ Created collection at ~/.skillmeat/collection/default
✓ Initialized collection.toml
✓ Ready to add artifacts
```

#### Workflow 2: Add Artifact from GitHub
```bash
# Add skill from GitHub
skillmeat add skill anthropics/skills/python@latest

# Add command from repo
skillmeat add command wshobson/commands/review@v1.2.0

# Add with custom name
skillmeat add agent obra/superpowers/code-review --name reviewer
```

**Expected Output:**
```
Fetching anthropics/skills/python@latest...
✓ Downloaded and validated
✓ Added to collection: python-skill
  Type: skill
  Version: latest → abc123d
  Upstream: https://github.com/anthropics/skills/python
```

#### Workflow 3: Add Artifact from Local Project
```bash
# From current project
cd ~/projects/my-app
skillmeat add command .claude/commands/custom-review.md

# From specific path
skillmeat add skill ~/.claude/skills/user/my-custom-skill
```

**Expected Output:**
```
✓ Copied from .claude/commands/custom-review.md
✓ Added to collection: custom-review
  Type: command
  No upstream (local origin)
```

#### Workflow 4: View Collection
```bash
# List all artifacts
skillmeat list

# Filter by type
skillmeat list --type command

# Show details
skillmeat show custom-review
```

**Expected Output (list):**
```
Collection: default (12 artifacts)

Commands (4):
  • custom-review        (local)         [modified today]
  • lint-check          github:wshobson  [synced]
  • security-scan       github:wshobson  [outdated ↑]
  • test-runner         github:anthropics [synced]

Skills (3):
  • python-skill        github:anthropics [synced]
  • javascript-helper   github:anthropics [synced]
  • canvas-design       github:anthropics [synced]

Agents (5):
  • code-reviewer       github:obra      [synced]
  • security-auditor    github:obra      [synced]
  • test-generator      local            [modified today]
  • doc-writer          github:wshobson  [synced]
  • refactor-assistant  github:wshobson  [outdated ↑]
```

**Expected Output (show):**
```
custom-review
─────────────────────────────────────────
Type:         command
Name:         custom-review
Description:  Comprehensive code review with security focus
Origin:       local
Added:        2025-11-01
Last Modified: 2025-11-05

Location in Collection:
  ~/.skillmeat/collection/default/commands/custom-review.md

Deployed to Projects:
  • ~/projects/web-app (.claude/commands/custom-review.md)
  • ~/projects/api-server (.claude/commands/custom-review.md)

Tags: review, security, quality

[View Source] [Edit] [Remove] [Deploy]
```

#### Workflow 5: Deploy to Project
```bash
# Deploy specific artifact
cd ~/projects/new-project
skillmeat deploy custom-review

# Deploy multiple
skillmeat deploy custom-review python-skill code-reviewer

# Deploy entire collection
skillmeat deploy --all

# Interactive selection
skillmeat deploy --interactive
```

**Expected Output:**
```
Deploying to ~/projects/new-project/.claude/

✓ custom-review → .claude/commands/custom-review.md
✓ python-skill → .claude/skills/python-skill/
✓ code-reviewer → .claude/agents/code-reviewer.md

Deployed 3 artifacts. Ready to use!
```

#### Workflow 6: Check for Updates
```bash
# Check all artifacts
skillmeat status

# Check specific artifact
skillmeat status python-skill

# Update specific artifact
skillmeat update python-skill

# Update all outdated
skillmeat update --all
```

**Expected Output (status):**
```
Checking upstream sources...

Outdated (2):
  • security-scan: v1.2.0 → v1.3.0 available
    Changes: Added OWASP Top 10 checks, improved performance
  • refactor-assistant: abc123d → def456e available
    Changes: 3 commits since your version

Synced (8):
  ✓ custom-review, lint-check, test-runner, python-skill,
    javascript-helper, canvas-design, code-reviewer, security-auditor

Modified Locally (2):
  ⚠ custom-review: Modified in collection, upstream not tracked
  ⚠ test-generator: Local-only artifact

Run 'skillmeat update --all' to update outdated artifacts
```

#### Workflow 7: Version Management
```bash
# Create snapshot
skillmeat snapshot "Before major refactor"

# List snapshots
skillmeat history

# Rollback
skillmeat rollback <snapshot-id>
```

**Expected Output (history):**
```
Collection Snapshots:

1. 2025-11-05 14:32  Before major refactor
   12 artifacts (current)

2. 2025-11-04 09:15  Added security tools
   10 artifacts

3. 2025-11-01 16:45  Initial setup
   5 artifacts

Use 'skillmeat rollback <number>' to restore a snapshot
```

### 4.3 Configuration Files

#### Collection Manifest (collection.toml)
```toml
[collection]
name = "default"
version = "1.0.0"
created = "2025-11-01T10:00:00Z"
updated = "2025-11-05T14:32:00Z"

[[artifacts]]
name = "custom-review"
type = "command"
path = "commands/custom-review.md"
origin = "local"
added = "2025-11-01T10:30:00Z"
tags = ["review", "security", "quality"]

[[artifacts]]
name = "python-skill"
type = "skill"
path = "skills/python-skill/"
origin = "github"
upstream = "https://github.com/anthropics/skills/tree/main/python"
version_spec = "latest"
resolved_sha = "abc123def456"
resolved_version = "v2.1.0"
added = "2025-11-02T14:00:00Z"
last_updated = "2025-11-03T09:15:00Z"
tags = ["python", "coding"]

[[artifacts]]
name = "code-reviewer"
type = "agent"
path = "agents/code-reviewer.md"
origin = "github"
upstream = "https://github.com/obra/superpowers/tree/main/agents/code-review"
version_spec = "v1.0.0"
resolved_sha = "789ghi012jkl"
added = "2025-11-02T15:30:00Z"
tags = ["review", "agent"]
```

#### Lock File (collection.lock)
```toml
# This file is auto-generated. Do not edit manually.

version = "1.0.0"
generated = "2025-11-05T14:32:00Z"

[[entries]]
name = "python-skill"
upstream = "https://github.com/anthropics/skills/tree/main/python"
resolved_sha = "abc123def456"
resolved_version = "v2.1.0"
fetched = "2025-11-03T09:15:00Z"

[[entries]]
name = "code-reviewer"
upstream = "https://github.com/obra/superpowers/tree/main/agents/code-review"
resolved_sha = "789ghi012jkl"
resolved_version = "v1.0.0"
fetched = "2025-11-02T15:30:00Z"
```

#### Deployment Tracking (per project)
```toml
# .claude/.skillmeat-deployed.toml

[[deployed]]
name = "custom-review"
from_collection = "default"
deployed_at = "2025-11-05T10:00:00Z"
path = "commands/custom-review.md"
collection_sha = "abc123"

[[deployed]]
name = "python-skill"
from_collection = "default"
deployed_at = "2025-11-05T10:00:00Z"
path = "skills/python-skill/"
collection_sha = "def456"
local_modifications = true
```

---

## 5. Technical Architecture

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (Click Framework)                         │
└─────────────────────────────────────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼────┐          ┌──────▼──────┐        ┌──────▼──────┐
│ Collection│        │  Deployment  │        │   Sync      │
│ Manager  │        │   Engine     │        │   Engine    │
└───┬────┘          └──────┬──────┘        └──────┬──────┘
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼────┐          ┌──────▼──────┐        ┌──────▼──────┐
│ Artifact│          │   Version   │        │   GitHub    │
│ Manager │          │   Manager   │        │   Client    │
└───┬────┘          └──────┬──────┘        └──────┬──────┘
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Storage Layer │
                    │  - Collection  │
                    │  - Lock Files  │
                    │  - Snapshots   │
                    └────────────────┘
```

### 5.2 Data Models

```python
@dataclass
class Collection:
    """Personal collection of Claude artifacts"""
    name: str
    version: str
    artifacts: List[Artifact]
    created: datetime
    updated: datetime

@dataclass
class Artifact:
    """Represents any Claude configuration artifact"""
    name: str
    type: ArtifactType  # skill, command, agent, mcp, hook
    path: Path  # relative to collection root
    origin: OriginType  # local, github
    upstream: Optional[str]  # source URL if from GitHub
    version_spec: Optional[str]  # latest, v1.0.0, branch name
    resolved_sha: Optional[str]  # for reproducibility
    resolved_version: Optional[str]  # tag/branch resolved
    metadata: ArtifactMetadata
    added: datetime
    last_updated: Optional[datetime]
    tags: List[str]

@dataclass
class ArtifactMetadata:
    """Extracted from artifact files"""
    title: Optional[str]
    description: Optional[str]
    author: Optional[str]
    license: Optional[str]
    dependencies: List[str]
    extra: Dict[str, Any]

@dataclass
class Deployment:
    """Tracks artifact deployment to project"""
    artifact_name: str
    from_collection: str
    deployed_at: datetime
    project_path: Path
    artifact_path: Path
    collection_sha: str  # SHA of artifact at deployment
    local_modifications: bool

@dataclass
class Snapshot:
    """Collection version snapshot"""
    id: str
    timestamp: datetime
    message: str
    collection_state: bytes  # serialized collection
```

### 5.3 Module Structure

```
skillmeat/
├── __init__.py
├── cli.py                      # Click command interface
├── core/
│   ├── __init__.py
│   ├── collection.py           # Collection management
│   ├── artifact.py             # Artifact operations
│   ├── deployment.py           # Deploy to projects
│   ├── sync.py                 # Bidirectional sync
│   └── version.py              # Snapshot & rollback
├── sources/
│   ├── __init__.py
│   ├── base.py                 # Abstract source interface
│   ├── github.py               # GitHub integration
│   └── local.py                # Local filesystem
├── storage/
│   ├── __init__.py
│   ├── manifest.py             # TOML reading/writing
│   ├── lockfile.py             # Lock file management
│   └── snapshot.py             # Snapshot storage
├── utils/
│   ├── __init__.py
│   ├── metadata.py             # Extract from files
│   ├── validator.py            # Validate artifacts
│   └── diff.py                 # Compare versions
└── config.py                   # User configuration

tests/
├── unit/
│   ├── test_collection.py
│   ├── test_artifact.py
│   ├── test_deployment.py
│   └── ...
├── integration/
│   ├── test_cli.py
│   ├── test_github_integration.py
│   └── ...
└── fixtures/
    ├── sample_skills/
    ├── sample_commands/
    └── sample_agents/
```

### 5.4 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.9+ | Existing codebase, great CLI libraries |
| **CLI Framework** | Click 8.0+ | Already in use, feature-rich |
| **Output** | Rich | Beautiful terminal output |
| **Config Format** | TOML | Human-readable, existing pattern |
| **Git Operations** | GitPython | Existing integration |
| **Testing** | pytest | Comprehensive framework |
| **Type Checking** | mypy | Catch errors early |
| **Packaging** | setuptools | Standard distribution |

**Web Interface (Phase 3):**
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend** | FastAPI | Modern Python API framework |
| **Frontend** | React + TypeScript | Rich UI capabilities |
| **Database** | SQLite | Embedded, no setup needed |
| **Authentication** | Optional OAuth | For cloud features only |

### 5.5 File Organization

```
~/.skillmeat/
├── config.toml                 # User configuration
├── collections/
│   ├── default/
│   │   ├── collection.toml     # Manifest
│   │   ├── collection.lock     # Lock file
│   │   ├── commands/           # Artifact storage
│   │   │   ├── custom-review.md
│   │   │   └── lint-check.md
│   │   ├── skills/
│   │   │   ├── python-skill/
│   │   │   │   └── SKILL.md
│   │   │   └── javascript-helper/
│   │   │       └── SKILL.md
│   │   └── agents/
│   │       ├── code-reviewer.md
│   │       └── security-auditor.md
│   └── web-dev/                # Named collection
│       ├── collection.toml
│       ├── collection.lock
│       └── ...
└── snapshots/
    ├── default/
    │   ├── 2025-11-05-143200.tar.gz
    │   ├── 2025-11-04-091500.tar.gz
    │   └── snapshots.toml      # Snapshot metadata
    └── web-dev/
        └── ...

# Per-project tracking
~/projects/my-app/.claude/
├── .skillmeat-deployed.toml    # Deployment tracking
├── commands/
│   └── custom-review.md        # Deployed artifact
├── skills/
│   └── python-skill/           # Deployed artifact
└── agents/
    └── code-reviewer.md        # Deployed artifact
```

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cold Start** | <2s for CLI commands | Time from invocation to output |
| **Collection List** | <500ms for 100 artifacts | Time to display list |
| **Deploy** | <5s for 10 artifacts | Time to copy files |
| **Update Check** | <10s for 20 GitHub sources | Time to check all upstreams |
| **Search** | <1s across 1000 artifacts | Cross-project search time |

### 6.2 Reliability

- **Data Safety**: Never lose artifact data (atomic operations, backups)
- **Idempotency**: Commands can be run multiple times safely
- **Error Handling**: Clear error messages, graceful degradation
- **Validation**: All inputs validated before operations
- **Testing**: >80% code coverage, CI on all commits

### 6.3 Usability

- **Discoverability**: `--help` on every command with examples
- **Feedback**: Progress indicators for long operations
- **Reversibility**: Undo/rollback for destructive operations
- **Documentation**: README with quickstart, command reference, troubleshooting
- **Conventions**: Follow Git-like command patterns

### 6.4 Security

- **Input Validation**: Sanitize paths, URLs, file contents
- **Sandboxing**: No arbitrary code execution during add/deploy
- **Token Security**: GitHub tokens stored securely, never logged
- **File Permissions**: Respect filesystem permissions
- **Dependency Security**: Dependabot for Python dependencies

### 6.5 Compatibility

- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13
- **OS**: macOS, Linux, Windows (WSL)
- **Claude**: Compatible with latest Claude Code/Desktop
- **Git**: Git 2.0+

### 6.6 Maintainability

- **Code Style**: Black formatter, flake8 linter
- **Type Hints**: Full type coverage, mypy checking
- **Documentation**: Docstrings on all public APIs
- **Testing**: Unit + integration + E2E tests
- **CI/CD**: Automated testing, releases, publishing

---

## 7. Success Criteria

### 7.1 MVP Launch Criteria

**Must Have:**
- ✅ All Phase 1 features implemented and tested
- ✅ CLI with 10+ core commands working
- ✅ Support for Skills, Commands, Agents (3 artifact types)
- ✅ GitHub source integration with version resolution
- ✅ Local source support (add from project)
- ✅ Deploy to project with tracking
- ✅ Update checking and basic update flow
- ✅ Snapshot and rollback functionality
- ✅ Comprehensive documentation (README, command help)
- ✅ >80% test coverage
- ✅ CI/CD pipeline operational
- ✅ Package published to PyPI

**Nice to Have:**
- ⭐ Interactive deploy mode (checkbox selection)
- ⭐ Rich diff display for updates
- ⭐ Bash/Zsh completion scripts
- ⭐ Migration tool from existing skillman installations

### 7.2 User Acceptance Criteria

**Core Workflows:**
1. User can initialize collection in <1 minute
2. User can add artifact from GitHub in <30 seconds
3. User can add artifact from local project in <15 seconds
4. User can deploy artifacts to new project in <1 minute
5. User can check for updates and update artifacts in <2 minutes
6. User can rollback collection to previous state in <30 seconds

**Quality:**
- Zero critical bugs blocking core workflows
- Average command response time <2s
- Error messages are actionable (tell user what to do)
- Help text is sufficient to complete tasks without docs

### 7.3 Technical Acceptance Criteria

- All unit tests passing (>80% coverage)
- All integration tests passing
- Type checking passes with mypy
- Linting passes with flake8
- Security scan passes (no high/critical vulnerabilities)
- Documentation builds without errors
- Package installs cleanly via pip
- Backwards compatible with Python 3.9+

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| **Scope Creep** | High | High | Strict MVP definition, defer Phase 2/3 features |
| **GitHub API Rate Limits** | Medium | Medium | Implement caching, support GitHub tokens, exponential backoff |
| **Merge Conflicts Complex** | High | Medium | Start with simple strategies (take upstream/keep local), defer 3-way merge to Phase 2 |
| **Performance at Scale** | Medium | Low | Lazy loading, pagination, index builds |
| **Windows Path Issues** | Medium | Medium | Use pathlib throughout, test on Windows CI |
| **User Confusion** | Medium | Medium | Invest in documentation, examples, error messages |
| **Competitor Launches** | Low | Low | Focus on differentiators (collections, personal use) |

---

## 9. Open Questions

1. **Collection Inheritance**: Should collections support inheritance (base → specialized)?
   - _Decision needed by: Phase 1 implementation_
   - _Leaning: Yes, but defer to Phase 2_

2. **Artifact Naming**: Allow duplicate names in collection if different types?
   - _Decision needed by: Phase 1 implementation_
   - _Leaning: No, enforce unique names across all types_

3. **Update Strategy Default**: What's the default when update conflicts with local modifications?
   - _Decision needed by: Phase 1 implementation_
   - _Leaning: Prompt user, no automatic overwrite_

4. **Web Interface Priority**: Deploy as SPA or server-rendered?
   - _Decision needed by: Phase 3 planning_
   - _Leaning: SPA with REST API_

5. **Cloud Sync**: Built-in or rely on Git?
   - _Decision needed by: Post-MVP_
   - _Leaning: Git for MVP, consider cloud in future_

---

## 10. Timeline & Milestones

### Phase 1: MVP (Weeks 1-8)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| **1-2** | Architecture & Setup | Refactor codebase, new module structure, CI/CD updates |
| **3-4** | Core Collection | Collection init, add (GitHub + local), list, show |
| **5-6** | Deployment & Tracking | Deploy command, tracking system, update checking |
| **7** | Versioning | Snapshot, history, rollback |
| **8** | Polish & Launch | Documentation, examples, PyPI publish, announcement |

### Phase 2: Intelligence (Weeks 9-14)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| **9-10** | Search & Analytics | Cross-project search, usage tracking, deduplication |
| **11-12** | Smart Updates | Merge strategies, conflict resolution UI |
| **13-14** | Bidirectional Sync | Sync from projects back to collection |

### Phase 3: Advanced (Weeks 15-20)

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| **15-17** | Web Interface | FastAPI backend, React frontend, deployment |
| **18-19** | Team Features | Collection sharing, recommendations |
| **20** | MCP & Ecosystem | MCP server management, marketplace browsing |

---

## 11. Dependencies

### External Dependencies

- **GitHub API**: For fetching repos, rate limits apply
- **Git CLI**: Must be installed on user system
- **Python Ecosystem**: PyPI for distribution
- **Claude Code**: Target platform, must stay compatible

### Internal Dependencies

- **Existing Codebase**: Refactor from skillman foundation
- **Testing Infrastructure**: Must maintain >80% coverage throughout
- **Documentation**: Keep in sync with features

---

## 12. Metrics & Analytics

### Usage Metrics (Telemetry - Opt-in)

- Command usage frequency
- Artifact types most used
- Average collection size
- Deployment frequency
- Update check frequency
- Error rates by command

### Success Metrics

- **Activation**: % of users who add first artifact within 7 days
- **Engagement**: Average commands per week
- **Retention**: % of users active 30 days after install
- **Growth**: Weekly active user growth rate
- **Satisfaction**: GitHub stars, issue closure time, community feedback

---

## Appendix A: Command Reference (MVP)

```bash
# Collection Management
skillmeat init                                  # Initialize default collection
skillmeat collection create <name>              # Create named collection
skillmeat collection list                       # List all collections
skillmeat collection use <name>                 # Switch active collection

# Adding Artifacts
skillmeat add skill <github-spec>              # Add skill from GitHub
skillmeat add command <github-spec>            # Add command from GitHub
skillmeat add agent <github-spec>              # Add agent from GitHub
skillmeat add <type> <local-path>              # Add from local filesystem
skillmeat add --interactive                    # Guided add workflow

# Viewing
skillmeat list                                 # List all artifacts
skillmeat list --type <type>                   # Filter by type
skillmeat list --tag <tag>                     # Filter by tag
skillmeat show <name>                          # Show artifact details

# Deployment
skillmeat deploy <name> [names...]             # Deploy specific artifacts
skillmeat deploy --all                         # Deploy entire collection
skillmeat deploy --interactive                 # Interactive selection
skillmeat deploy --project <path>              # Deploy to specific project

# Updates
skillmeat status                               # Check update status
skillmeat status <name>                        # Check specific artifact
skillmeat update <name>                        # Update specific artifact
skillmeat update --all                         # Update all outdated

# Versioning
skillmeat snapshot [message]                   # Create snapshot
skillmeat history                              # List snapshots
skillmeat rollback <snapshot-id>               # Rollback to snapshot

# Removal
skillmeat remove <name>                        # Remove from collection
skillmeat undeploy <name> [--project <path>]   # Remove from project

# Configuration
skillmeat config list                          # List all settings
skillmeat config set <key> <value>             # Set configuration
skillmeat config get <key>                     # Get configuration

# Utilities
skillmeat validate <path>                      # Validate artifact structure
skillmeat help [command]                       # Show help
skillmeat version                              # Show version
```

---

## Appendix B: Glossary

- **Artifact**: Any Claude Code configuration file (Skill, Command, Agent, MCP server, Hook)
- **Collection**: Personal library of artifacts maintained by SkillMeat
- **Deployment**: Copying artifacts from collection to project's .claude/ directory
- **Origin**: Source type of artifact (local, github)
- **Upstream**: Original GitHub repository for an artifact
- **Snapshot**: Point-in-time backup of entire collection
- **Manifest**: collection.toml file describing collection contents
- **Lock File**: collection.lock file with resolved versions for reproducibility
- **Scope**: User-level (~/.claude/) vs project-level (.claude/)
- **Fork**: Local modification of artifact from upstream source
- **Sync**: Bidirectional reconciliation between collection and projects

---

## Appendix C: Migration from Skillman

For existing skillman users, we'll provide migration utilities:

```bash
# Migrate existing skills.toml to collection
skillmeat migrate --from-skillman [path]

# Import installed skills to collection
skillmeat import --from-claude-dir ~/.claude/skills/user
skillmeat import --from-claude-dir ./.claude/skills

# Expected behavior:
# - Create collection if not exists
# - Import all artifacts with metadata preservation
# - Maintain upstream tracking if available
# - Create initial snapshot
```

---

**Document History:**
- v1.0 (2025-11-05): Initial PRD for MVP definition
