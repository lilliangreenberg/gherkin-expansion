# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**gherkin-expansion** is a meta-project for BDD (Behavior-Driven Development) CLI tool creation. It contains:

1. **BDD Implementation Guide**: Comprehensive guide for implementing CLI applications using Gherkin specifications and Behave
2. **Claude Code Skills**: Reusable skills for automating BDD project initialization
3. **Template Infrastructure**: Git-based template system for cookiecutter project generation

This project does not contain application code itself—it's a framework for creating BDD-based CLI applications.

## Project Structure

```
gherkin-expansion/
├── BDD_IMPLEMENTATION_GUIDE.md     # Complete BDD workflow documentation
├── skills/                          # Claude Code skills
│   ├── init-bdd-project/           # v1.0: Script-based initialization
│   │   ├── SKILL.md
│   │   └── scripts/init_project.py
│   └── init-project-cookiecutter/  # v2.0: Git-based cookiecutter (CURRENT)
│       ├── SKILL.md                # Complete skill documentation
│       ├── README.md               # Quick start guide
│       └── scripts/
│           ├── init_project.py     # Main orchestration script
│           └── template_sources.yaml  # Git repository mappings
├── main.py                          # Placeholder (not used)
├── pyproject.toml                   # Project metadata
└── README.md                        # Project documentation
```

## Key Architecture: Git-Based Templates

### How It Works

The **init-project-cookiecutter** skill (v2.0) uses a distributed, Git-based template architecture:

```
User Requirements
      ↓
Template Selection (from template_sources.yaml)
      ↓
Git URL Resolution (gh:org/repo)
      ↓
Cookiecutter Fetch (clone from Git)
      ↓
Project Generation
      ↓
Post-Setup (git init, uv sync)
```

**Key Innovation**: Templates are NOT stored locally. They live in Git repositories and are referenced by URL in `template_sources.yaml`.

### Why Git-Based?

1. **Distributed**: Templates can be in any Git repository
2. **Versioned**: Use branches/tags for template versions
3. **Collaborative**: Multiple teams can maintain templates independently
4. **Extensible**: Add new templates by editing YAML config
5. **No Duplication**: Don't need template copies in this repo

## Available Skills

### 1. init-bdd-project (v1.0 - Legacy)

**Location**: `skills/init-bdd-project/`
**Approach**: Python script generates project structure directly
**Status**: Functional but deprecated in favor of v2.0

**Use when**: Simple, self-contained initialization without external dependencies

### 2. init-project-cookiecutter (v2.0 - Current)

**Location**: `skills/init-project-cookiecutter/`
**Approach**: Cookiecutter + Git repositories
**Status**: Active, recommended

**Use when**: You need flexible, version-controlled, distributed templates

**Quick Start**:
```bash
cd skills/init-project-cookiecutter
python scripts/init_project.py --interactive
```

## Common Development Tasks

### Initialize a New BDD CLI Project

```bash
# Interactive mode (recommended)
cd skills/init-project-cookiecutter
python scripts/init_project.py --interactive

# Non-interactive mode
python scripts/init_project.py \
    --name "my-project" \
    --framework "click" \
    --integrations "api,files"
```

### List Available Templates

```bash
cd skills/init-project-cookiecutter
python scripts/init_project.py --list-templates
```

### Add a Custom Template

Edit `skills/init-project-cookiecutter/scripts/template_sources.yaml`:

```yaml
templates:
  my-custom-template:
    name: "My Custom BDD Template"
    git_url: "gh:your-org/your-template-repo"
    framework: "click"
    supports_integrations:
      - api
      - files
    priority: 10
    status: "experimental"
```

### Test a Template from Git

```bash
python scripts/init_project.py \
    --name "test-project" \
    --template-url "gh:org/template-repo"
```

## Template Sources Configuration

**File**: `skills/init-project-cookiecutter/scripts/template_sources.yaml`

This YAML file maps project requirements → Git repository URLs. It defines:

- Available templates and their Git URLs
- Which CLI frameworks each template supports
- Which integrations (api, database, files, data) are supported
- Template selection priority
- Version/branch information (checkout field)

**Example**:
```yaml
templates:
  bdd-cli-click:
    name: "BDD CLI with Click Framework"
    git_url: "gh:your-org/bdd-cli-click-template"
    directory: "optional/subdirectory"  # If template in subdirectory
    checkout: "v2.0.0"                   # Branch, tag, or commit
    framework: "click"
    supports_integrations:
      - api
      - database
      - files
      - data
    priority: 1
    status: "stable"
```

## Template Repository Patterns

### Pattern 1: Dedicated Template Repo
One template per repository.

```
github.com/org/bdd-cli-click-template/
├── cookiecutter.json
├── hooks/
│   ├── pre_gen_project.py
│   └── post_gen_project.py
└── {{cookiecutter.project_slug}}/
    ├── src/
    ├── tests/
    ├── features/
    └── pyproject.toml
```

### Pattern 2: Monorepo with Multiple Templates
Multiple templates in subdirectories.

```
github.com/org/python-templates/
├── cli-templates/
│   ├── bdd-click/
│   │   └── cookiecutter.json
│   ├── bdd-typer/
│   │   └── cookiecutter.json
│   └── bdd-argparse/
│       └── cookiecutter.json
```

### Pattern 3: Versioned Templates
Use Git tags/branches for versions.

```
github.com/org/bdd-template/
  main branch (latest)
  develop branch (bleeding edge)
  tags: v1.0.0, v2.0.0, v2.1.0
```

## BDD Workflow

For complete BDD workflow documentation, see **BDD_IMPLEMENTATION_GUIDE.md**.

### Quick Summary

1. **Write Gherkin Features**: Define behavior in plain language
2. **Run Tests (Red)**: Behave shows undefined steps
3. **Implement Step Definitions**: Connect Gherkin to Python
4. **Run Tests (Still Red)**: Steps pass, but no implementation
5. **Implement Code (Green)**: Write minimal code to pass
6. **Refactor**: Improve while keeping tests green
7. **Repeat**: Next scenario

### BDD Project Structure

Generated projects follow this structure:

```
my-project/
├── src/my_project/
│   ├── core/              # Domain models
│   ├── infrastructure/    # External integrations (API, DB, files)
│   ├── services/          # Business logic
│   ├── cli/              # CLI interface
│   └── config/           # Configuration
├── tests/
│   ├── unit/             # pytest unit tests
│   └── integration/      # pytest integration tests
├── features/             # Behave BDD tests
│   ├── *.feature        # Gherkin scenarios
│   ├── steps/           # Step definitions
│   ├── environment.py   # Test hooks
│   └── behave.ini       # Behave configuration
├── pyproject.toml       # Dependencies and config
└── README.md
```

## Integration Types

Projects can include these integrations:

### api
- HTTP/REST API client functionality
- Adds: `httpx`, `responses` (for mocking)
- Modules: `infrastructure/api_client.py`
- Features: `features/04_api_integration.feature`

### database
- Database operations with SQLAlchemy ORM
- Adds: `sqlalchemy`, `psycopg2-binary`
- Modules: `infrastructure/database.py`, `core/models.py`
- Features: `features/05_database_operations.feature`

### files
- Advanced file processing (PDFs, images, etc.)
- Adds: `pypdf2`, `python-magic-bin`
- Modules: `infrastructure/file_handler.py`
- Features: `features/03_file_operations.feature`

### data
- Data analysis and transformation
- Adds: `pandas`, `numpy`
- Modules: `services/data_processor.py`
- Features: `features/06_data_processing.feature`

## CLI Framework Comparison

### Click (Priority 1)
- **Best for**: Feature-rich CLIs with many subcommands
- **Style**: Decorator-based
- **Pros**: Most popular, excellent docs, rich features
- **Cons**: External dependency

### Typer (Priority 2)
- **Best for**: Modern type-hint driven CLIs
- **Style**: Function parameters with type hints
- **Pros**: Automatic validation, beautiful help, FastAPI-style
- **Cons**: Newer, smaller community

### Argparse (Priority 3)
- **Best for**: Minimal dependencies, maximum portability
- **Style**: Imperative parser configuration
- **Pros**: Standard library, no dependencies
- **Cons**: More verbose, manual help formatting

## Development Tools Used

### Package Management
- **uv**: Fast Python package installer (recommended)
  ```bash
  uv venv              # Create virtual environment
  uv sync              # Install dependencies
  uv add <package>     # Add dependency
  ```

### Code Quality
- **ruff**: Fast linter and formatter
  ```bash
  uv run ruff check .      # Lint
  uv run ruff format .     # Format
  ```

- **mypy**: Static type checking
  ```bash
  uv run mypy src/ --strict
  ```

### Testing
- **pytest**: Unit and integration tests
  ```bash
  uv run pytest
  uv run pytest --cov     # With coverage
  ```

- **behave**: BDD/Gherkin tests
  ```bash
  uv run behave
  uv run behave --tags=@wip     # Work in progress
  uv run behave --tags=@passing # All passing tests
  ```

## Important Conventions

### Template Variable Naming
In cookiecutter templates, use these standard variables:
- `project_name`: Human-readable name
- `project_slug`: Python package name (snake_case)
- `project_short_description`: One-line description
- `cli_framework`: "click", "typer", or "argparse"
- `has_api_integration`: "yes" or "no"
- `has_database_integration`: "yes" or "no"
- `has_files_integration`: "yes" or "no"
- `has_data_integration`: "yes" or "no"
- `author_name`: Author's name
- `author_email`: Author's email
- `python_version`: "3.11"

### Git URL Formats
Cookiecutter supports:
- `gh:username/repo` (GitHub shorthand)
- `gl:username/repo` (GitLab shorthand)
- `bb:username/repo` (Bitbucket shorthand)
- `https://github.com/username/repo.git` (Full URL)
- `git@github.com:username/repo.git` (SSH URL)

### Gherkin Tag Conventions
- `@wip`: Work in progress (currently implementing)
- `@passing`: Fully implemented and passing
- `@failing`: Not yet implemented
- `@smoke`: Critical path tests
- `@integration`: Integration tests (vs unit)

## Error Handling

When working with the cookiecutter skill:

### TemplateNotFoundError
**Cause**: No template matches requirements
**Solution**: Check available templates with `--list-templates`, adjust requirements, or add template to `template_sources.yaml`

### GitCloneError
**Cause**: Failed to clone template repository
**Solution**: Verify Git URL, check network, test with `git clone <url>`, ensure repository is accessible

### IntegrationNotSupportedError
**Cause**: Template doesn't support requested integration
**Solution**: Choose different template or remove integration from requirements

### PrerequisiteError
**Cause**: Missing required tools (cookiecutter, git, uv)
**Solution**: Install missing tools (see Prerequisites section)

## Prerequisites for Generated Projects

Generated BDD CLI projects require:

```bash
# Python 3.11+
python --version

# uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# git (version control)
git --version
```

## Adding New Features to This Project

### Adding a New Skill

1. Create skill directory:
   ```bash
   mkdir -p skills/my-new-skill/scripts
   ```

2. Create SKILL.md documenting the skill

3. Create implementation script in `scripts/`

4. Test the skill:
   ```bash
   python skills/my-new-skill/scripts/main.py
   ```

### Adding a New Template Source

1. Create the template repository with cookiecutter structure

2. Push to Git:
   ```bash
   git remote add origin git@github.com:org/my-template.git
   git push -u origin main
   ```

3. Register in `template_sources.yaml`:
   ```yaml
   templates:
     my-template:
       name: "My Template"
       git_url: "gh:org/my-template"
       framework: "click"
       supports_integrations: ["api"]
   ```

4. Test:
   ```bash
   python scripts/init_project.py --name "test" --template-url "gh:org/my-template"
   ```

## Files to NOT Modify

- `main.py`: Placeholder only, not used
- `skills/init-bdd-project/`: Legacy skill, kept for reference
- Generated `.python-version`: Auto-generated

## Files That Guide AI Behavior

- **This file (CLAUDE.md)**: High-level project guidance
- **skills/*/SKILL.md**: Detailed skill documentation
- **BDD_IMPLEMENTATION_GUIDE.md**: Complete BDD workflow
- **User's ~/.claude/CLAUDE.md**: User's global preferences (take precedence)

## Troubleshooting

### "cookiecutter: command not found"
```bash
pip install cookiecutter
# Or: uv tool install cookiecutter
# Or: pipx install cookiecutter
```

### Git Clone Issues
```bash
# Test SSH
ssh -T git@github.com

# Use HTTPS instead
git_url: "https://github.com/org/repo.git"
```

### Python Version Issues
```bash
# Check version
python --version

# Update if needed (macOS with Homebrew)
brew install python@3.11

# Or download from python.org
```

### YAML Syntax Errors
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('template_sources.yaml'))"
```

## Philosophy

This project embodies:

1. **Separation of Concerns**: Templates separate from orchestration
2. **Distributed Architecture**: Templates can live anywhere (Git)
3. **Declarative Configuration**: YAML over code for mappings
4. **Outside-In Development**: Start with behavior (Gherkin), implement inward
5. **Minimal Coupling**: Skills are independent, reusable
6. **Version Control Everything**: Templates, configs, generated code

## References

- **Cookiecutter**: https://cookiecutter.readthedocs.io/
- **Behave (BDD)**: https://behave.readthedocs.io/
- **Gherkin**: https://cucumber.io/docs/gherkin/
- **uv Package Manager**: https://docs.astral.sh/uv/
- **Claude Code**: https://claude.com/claude-code

## Support

For issues with:
- **This project**: Check BDD_IMPLEMENTATION_GUIDE.md
- **Specific skill**: Check that skill's SKILL.md
- **Cookiecutter**: https://github.com/cookiecutter/cookiecutter
- **Generated projects**: Check the project's README.md and features/
