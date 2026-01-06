---
name: init-bdd-project
description: Initialize a new BDD-based CLI project from scratch with complete directory structure, Behave configuration, pyproject.toml, and template feature files. Use this skill when creating a new CLI application that will use BDD/Gherkin specifications with Behave for testing. Supports Click, Typer, and argparse frameworks with optional API, database, or file processing integrations.
compatibility: Requires uv package manager. Python 3.11+ recommended. Works on macOS, Linux, and Windows.
license: MIT
metadata:
  automation_level: full
  skill_category: project-initialization
  version: 1.0.0
---

# init-bdd-project Skill

## Purpose

This skill automates the complete initialization of a BDD-based CLI project following best practices outlined in the Universal BDD Guide. It creates a production-ready project structure with:

- Complete directory layout (src/, tests/, features/)
- Configured pyproject.toml with all necessary dependencies
- Behave environment setup with domain-specific hooks
- Template feature files based on the BDD workflow
- Pre-configured tooling (ruff, mypy, pytest, behave)
- .gitignore with standard exclusions

## When to Use This Skill

Use this skill when:
- Starting a new CLI application project
- You want to use BDD/Gherkin specifications with Behave
- You need a structured, test-driven development approach
- You're building tools for data processing, API clients, file management, or system automation
- You want industry best practices baked in from day one

## For AI Agents: How to Invoke This Skill

### Skill Location

This skill should be installed in one of these locations:
- User's Claude Code skills directory: `~/.claude/skills/init-bdd-project/`
- Project-local skills directory: `{project_root}/.claude/skills/init-bdd-project/`
- Working directory: `{cwd}/init-bdd-project/`

### Determining the Skill Path

Before invoking, check if the skill exists:

```bash
# Check common locations
if [ -f ~/.claude/skills/init-bdd-project/scripts/init_project.py ]; then
    SKILL_PATH=~/.claude/skills/init-bdd-project
elif [ -f ./.claude/skills/init-bdd-project/scripts/init_project.py ]; then
    SKILL_PATH=./.claude/skills/init-bdd-project
elif [ -f ./init-bdd-project/scripts/init_project.py ]; then
    SKILL_PATH=./init-bdd-project
else
    echo "Error: init-bdd-project skill not found"
    exit 1
fi
```

### Invocation Command

Use one of these approaches:

**Option 1: Using uv run (recommended)**
```bash
uv run python ${SKILL_PATH}/scripts/init_project.py \
    --name "my-project" \
    --framework "click" \
    --domain "data processing" \
    --integrations "api,files"
```

**Option 2: Direct Python (if uv not available)**
```bash
python3 ${SKILL_PATH}/scripts/init_project.py \
    --name "my-project" \
    --framework "click" \
    --domain "data processing" \
    --integrations "api,files"
```

**Option 3: Using absolute path**
```bash
python3 /Users/username/.claude/skills/init-bdd-project/scripts/init_project.py \
    --name "my-project" \
    --framework "click"
```

### Working Directory Considerations

- The script creates the project directory **relative to where it's executed**
- By default, it creates in the current working directory
- Use `--path` flag to specify a different base directory:

```bash
uv run python ${SKILL_PATH}/scripts/init_project.py \
    --name "my-project" \
    --framework "typer" \
    --path "/Users/username/projects"
```

### Prerequisites Check

The script will automatically check for:
- ✅ `uv` command availability
- ✅ Python 3.11+ version
- ⚠️ `git` (warning only, not fatal)

If prerequisites are missing, the script will fail fast with installation instructions.

### Complete Agent Workflow

Here's the complete flow an AI agent should follow:

```bash
# 1. Locate the skill
SKILL_PATH="./init-bdd-project"  # Adjust based on actual location

# 2. Gather user requirements (see Required Inputs section below)
PROJECT_NAME="data-validator"
FRAMEWORK="click"
DOMAIN="data validation tool"
INTEGRATIONS="files"

# 3. Invoke the skill
uv run python ${SKILL_PATH}/scripts/init_project.py \
    --name "${PROJECT_NAME}" \
    --framework "${FRAMEWORK}" \
    --domain "${DOMAIN}" \
    --integrations "${INTEGRATIONS}"

# 4. Navigate to created project
cd "${PROJECT_NAME}"

# 5. Initialize git repository
git init
git add .
git commit -m "Initial project structure from init-bdd-project skill"

# 6. Set up Python environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# 7. Verify installation
uv run ruff check .
uv run mypy src/
uv run pytest tests/
uv run behave

# 8. Report completion to user
echo "✓ Project ${PROJECT_NAME} initialized successfully!"
```

### Error Handling

The script may raise these errors:

| Error | Reason | Solution |
|-------|--------|----------|
| `RuntimeError: uv is not installed` | Missing uv package manager | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `RuntimeError: Python 3.11+ is required` | Python version too old | Upgrade Python to 3.11+ |
| `ValueError: Invalid project name` | Project name contains invalid characters | Use lowercase letters, numbers, underscores only |
| `FileExistsError: Directory already exists` | Target directory already exists | Choose different name or remove existing directory |
| `ValueError: Invalid integrations` | Unknown integration specified | Use only: api, database, files, data |

## Required Inputs

The skill will gather the following information from you:

1. **project_name** (required): The name of your project (e.g., "data-validator", "api-client")
   - Must be a valid Python package name (lowercase, underscores allowed)
   - Will be used for directory names and package structure

2. **cli_framework** (required): Choose one:
   - `click`: Full-featured, decorator-based CLI framework (most popular)
   - `typer`: Modern, type-hint based CLI framework (Click-powered)
   - `argparse`: Python standard library (minimal dependencies)

3. **domain** (optional): Domain/purpose of your CLI tool:
   - Examples: "data processing", "API client", "file converter", "deployment tool"
   - Helps customize template features and documentation
   - If not provided, creates generic templates

4. **integrations** (optional): List of external integrations your CLI will use:
   - `api`: HTTP/REST API integrations (adds httpx, responses for mocking)
   - `database`: Database operations (adds sqlalchemy, psycopg2)
   - `files`: File processing beyond basic I/O (adds pypdf2, python-magic)
   - `data`: Data analysis/transformation (adds pandas, numpy)
   - Can select multiple (e.g., ["api", "files"])

## Output

Creates a complete project structure:

```
{project_name}/
├── src/
│   └── {project_name}/
│       ├── __init__.py
│       ├── core/              # Domain models
│       ├── infrastructure/    # External integrations
│       ├── services/          # Business logic
│       ├── cli/              # CLI interface
│       └── config/           # Configuration
├── tests/
│   ├── unit/                 # pytest unit tests
│   └── integration/          # pytest integration tests
├── features/                 # Behave BDD tests
│   ├── 01_foundation.feature
│   ├── environment.py
│   ├── behave.ini
│   └── steps/
│       ├── __init__.py
│       └── common_steps.py
├── pyproject.toml           # Complete with dependencies
├── README.md                # Project documentation
├── .gitignore              # Standard exclusions
└── .python-version         # Python version specification
```

## Implementation Steps

### Step 1: Gather Requirements

Ask the user for required inputs if not already provided:
- project_name (validate it's a valid Python package name)
- cli_framework (present as a choice: click, typer, or argparse)
- domain (optional, ask for a brief description)
- integrations (optional, multi-select from: api, database, files, data)

### Step 2: Validate Inputs

- Ensure project_name is valid (lowercase, no hyphens, valid Python identifier)
- Ensure the target directory doesn't already exist
- Convert project_name to snake_case if needed

### Step 3: Create Directory Structure

Execute the project initialization script. See the "For AI Agents: How to Invoke This Skill" section above for detailed invocation instructions.

```bash
# Determine skill path (see agent invocation section for details)
SKILL_PATH="./init-bdd-project"  # Or use absolute path

# Execute the initialization
uv run python ${SKILL_PATH}/scripts/init_project.py \
  --name "{project_name}" \
  --framework "{cli_framework}" \
  --domain "{domain}" \
  --integrations "{integrations}"
```

**Note**: The script will automatically:
- Check prerequisites (uv, Python 3.11+)
- Validate project name
- Create all directory structures
- Generate configuration files
- Set up Behave environment
- Create template features

### Step 4: Initialize Git Repository

```bash
cd {project_name}
git init
git add .
git commit -m "Initial project structure from init-bdd-project skill"
```

### Step 5: Set up Python Environment

```bash
cd {project_name}
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv sync
```

### Step 6: Verify Installation

Run basic checks to ensure everything is set up correctly:

```bash
uv run ruff check .        # Should pass (no code yet)
uv run mypy src/          # Should pass
uv run pytest tests/      # Should pass (no tests yet)
uv run behave             # Should show 0 scenarios
```

### Step 7: Report Completion

Provide the user with:
- Summary of what was created
- Next steps for development
- Link to BDD_IMPLEMENTATION_GUIDE.md for workflow guidance

## Example Usage

### Example 1: Simple CLI Tool

```
User: "I need to create a new CLI tool for validating data files"

Agent: <uses init-bdd-project skill>
  - Asks for project name: "data-validator"
  - Asks for CLI framework: "click"
  - Asks for domain: "data validation"
  - Asks for integrations: ["files"]

Agent: <creates complete project structure>

Output:
  ✓ Created data-validator/ with complete BDD structure
  ✓ Installed dependencies: click, pydantic, behave, pytest, ruff, mypy
  ✓ Added file processing dependencies: pypdf2, python-magic
  ✓ Created template features for data validation domain
  ✓ Initialized git repository
  ✓ All checks passing

Next steps:
  1. cd data-validator
  2. Review features/01_foundation.feature
  3. Follow BDD workflow in BDD_IMPLEMENTATION_GUIDE.md
```

### Example 2: API Client

```
User: "Create a new project for a REST API client that needs database caching"

Agent: <uses init-bdd-project skill>
  - project_name: "api-client"
  - cli_framework: "typer"
  - domain: "REST API client with caching"
  - integrations: ["api", "database"]

Agent: <creates complete project structure>

Output:
  ✓ Created api-client/ with typer framework
  ✓ Added HTTP client dependencies: httpx, responses
  ✓ Added database dependencies: sqlalchemy, psycopg2
  ✓ Created template features for API client workflows
  ✓ Environment configured with API mocking and database test isolation

Next steps:
  1. cd api-client
  2. Define your API integration in features/04_external_integrations.feature
  3. Implement using the BDD red-green-refactor cycle
```

## Common Patterns

### After Creating a Project

1. **Review Generated Features**: Check `features/01_foundation.feature` for initial scenarios
2. **Customize Environment**: Edit `features/environment.py` for domain-specific setup
3. **Add Dependencies**: Run `uv add <package>` for additional needs
4. **Start Development**: Tag first scenario as @wip and begin BDD cycle

### Integration with Other Skills

This skill works well with:
- `bdd-cycle`: Implement individual scenarios
- `generate-step-definitions`: Create step definitions from features
- `setup-behave-env`: Further customize the Behave environment
- `review-gherkin-quality`: Validate your feature files

## Troubleshooting

### "Project directory already exists"
- Choose a different project name
- Remove the existing directory if it was a failed attempt
- Use `--force` flag to override (not recommended)

### "Invalid project name"
- Use lowercase letters, numbers, and underscores only
- Start with a letter
- No hyphens (hyphens are fine for the skill name, but not Python packages)

### "uv command not found"
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart your shell
- Verify: `uv --version`

### Dependencies fail to install
- Check Python version (3.11+ recommended)
- Ensure uv is up to date: `uv self update`
- Check internet connection
- Try: `uv sync --refresh`

## Technical Details

### Dependencies Added by Default

**Core Dependencies**:
- pydantic: Data validation and settings
- structlog: Structured logging
- rich: Terminal formatting
- pyyaml: Configuration files
- toml: TOML support

**CLI Framework** (one of):
- click
- typer
- (argparse is stdlib, no install needed)

**Development Dependencies**:
- pytest: Unit testing
- pytest-cov: Coverage reporting
- pytest-mock: Mocking support
- mypy: Static type checking
- ruff: Linting and formatting
- behave: BDD testing
- freezegun: Time mocking for tests

**Integration-Specific** (based on selections):
- **api**: httpx, responses
- **database**: sqlalchemy, psycopg2-binary
- **files**: pypdf2, python-magic-bin
- **data**: pandas, numpy

### Project Structure Philosophy

The structure follows:
- **XDG Base Directory**: Standard file locations
- **src/ layout**: Prevents accidental imports
- **Domain-Driven Design**: Separate core, infrastructure, services
- **Test Pyramid**: Unit > Integration > BDD
- **Progressive Feature Files**: Numbered for implementation order

## Best Practices

1. **Start Simple**: Begin with foundation features, add complexity incrementally
2. **Follow BDD Cycle**: Red → Green → Refactor for each scenario
3. **Tag Properly**: Use @wip, @passing, @failing to track progress
4. **Document as You Go**: Update README with actual usage
5. **Commit Often**: Each passing scenario is a commit-worthy milestone

## Reference

This skill implements the initialization strategy from:
- **BDD_IMPLEMENTATION_GUIDE.md**: Part 2 (Project Setup and Structure)
- **agentskills.io**: Anthropic Skills Specification

For the complete BDD workflow after initialization, refer to BDD_IMPLEMENTATION_GUIDE.md sections on:
- Part 3: Setting Up Behave
- Part 4: Writing Step Definitions
- Part 5: Implementation Strategy
