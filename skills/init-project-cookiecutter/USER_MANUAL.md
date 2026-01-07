# User Manual: init-project-cookiecutter

**Version 2.0.0**
**Last Updated**: January 2026

A comprehensive guide to initializing BDD-based CLI projects using Git-distributed cookiecutter templates.

---

## Table of Contents

1. [Introduction](#introduction)
2. [What This Skill Does](#what-this-skill-does)
3. [How It Works](#how-it-works)
4. [Installation & Setup](#installation--setup)
5. [Quick Start Guide](#quick-start-guide)
6. [Detailed Usage](#detailed-usage)
7. [Understanding Templates](#understanding-templates)
8. [Template Management](#template-management)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)
13. [Examples & Recipes](#examples--recipes)
14. [Reference](#reference)

---

## Introduction

### What Problem Does This Solve?

Starting a new CLI (Command-Line Interface) project with proper testing, structure, and best practices is time-consuming. You need to:

- Set up project structure (directories, files)
- Configure dependencies and build tools
- Create testing infrastructure (BDD/Behave)
- Write boilerplate code for CLI framework
- Set up linting, type checking, and code quality tools
- Configure git repository
- Write initial documentation

This skill **automates all of that** by generating a complete, production-ready BDD CLI project in seconds.

### Who Is This For?

- **Python developers** building CLI tools
- **Teams** wanting consistent project structure
- **BDD practitioners** using Gherkin and Behave
- **DevOps engineers** creating automation tools
- **Anyone** who wants to save hours of initial project setup

### What You Get

A fully configured project with:

✅ **Proper Python package structure** (src/ layout)
✅ **BDD testing setup** (Behave + Gherkin features)
✅ **CLI framework integrated** (Click, Typer, or argparse)
✅ **Unit & integration test structure** (pytest)
✅ **Code quality tools configured** (ruff, mypy)
✅ **Git repository initialized**
✅ **Virtual environment ready**
✅ **Dependencies installed**
✅ **Documentation templates**

All ready to start developing immediately!

---

## What This Skill Does

### The 30-Second Explanation

This skill asks you a few questions (project name, CLI framework, what integrations you need), then:

1. **Selects** the appropriate project template from Git repositories
2. **Fetches** that template using cookiecutter
3. **Generates** a complete project structure customized for your needs
4. **Initializes** git repository and virtual environment
5. **Installs** all dependencies
6. **Verifies** everything works

You get a working project in under a minute.

### The Detailed Explanation

#### What Makes This Different?

**Traditional Approach**: Copy/paste an old project, manually modify files, hope you didn't miss anything.

**This Skill's Approach**:

1. **Templates in Git**: Project templates live in version-controlled Git repositories, not on your local machine
2. **Distributed Architecture**: Templates can be in different repos, managed by different teams
3. **Smart Selection**: Automatically picks the right template based on your requirements
4. **Dynamic Fetching**: Downloads templates on-demand (with optional caching)
5. **Customization**: Templates are parameterized - your project name, settings, integrations all configured automatically

#### Key Innovation: Git-Based Templates

Instead of storing templates locally, this skill references templates by **Git URL**:

```yaml
# In configuration file
templates:
  bdd-cli-click:
    git_url: "gh:your-org/bdd-cli-click-template"
```

**Benefits**:
- Templates can be updated independently
- Multiple teams can maintain different templates
- Easy to add new templates (just add a URL)
- Version control (use branches/tags for versions)
- No duplication (templates don't need to be copied into this project)

---

## How It Works

### Architecture Overview

```
┌─────────────────┐
│  You (User)     │
│  - Project name │
│  - Framework    │
│  - Integrations │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Template Selection Engine  │
│  - Loads config from YAML   │
│  - Matches requirements     │
│  - Selects best template    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Git Repository             │
│  (Template Storage)         │
│  - Cookiecutter structure   │
│  - Parameterized files      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Cookiecutter               │
│  - Clones template          │
│  - Processes variables      │
│  - Generates files          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Post-Generation Setup      │
│  - Git init                 │
│  - Create venv              │
│  - Install dependencies     │
│  - Verify tests             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Your New Project!          │
│  Ready to code              │
└─────────────────────────────┘
```

### Components Explained

#### 1. The Skill Script (`init_project.py`)

**What it does**: Orchestrates the entire process

**Key responsibilities**:
- Collects user requirements (interactively or via command-line args)
- Validates inputs
- Selects appropriate template
- Invokes cookiecutter with correct parameters
- Runs post-generation setup

**Location**: `skills/init-project-cookiecutter/scripts/init_project.py`

#### 2. Template Registry (`template_sources.yaml`)

**What it does**: Maps requirements to Git repository URLs

**Contains**:
- List of available templates
- Git URLs for each template
- Framework compatibility info
- Supported integrations
- Template priority/selection rules

**Location**: `skills/init-project-cookiecutter/scripts/template_sources.yaml`

**Example entry**:
```yaml
templates:
  bdd-cli-click:
    name: "BDD CLI with Click Framework"
    description: "Full-featured BDD-based CLI using Click"
    git_url: "gh:your-org/bdd-cli-click-template"
    framework: "click"
    supports_integrations:
      - api
      - database
      - files
      - data
    priority: 1
    status: "stable"
```

#### 3. Cookiecutter Templates (In Git Repos)

**What they are**: Parameterized project templates

**Structure**:
```
template-repo/
├── cookiecutter.json          # Variables/parameters
├── hooks/
│   ├── pre_gen_project.py    # Validation before generation
│   └── post_gen_project.py   # Setup after generation
└── {{cookiecutter.project_slug}}/
    ├── src/                   # Source code
    ├── tests/                 # Unit/integration tests
    ├── features/              # BDD tests
    ├── pyproject.toml         # Dependencies
    └── README.md              # Documentation
```

**Variables** (in `cookiecutter.json`):
```json
{
  "project_name": "My Project",
  "project_slug": "my_project",
  "author_name": "Your Name",
  "has_api_integration": "yes",
  "has_database_integration": "no"
}
```

**Template files** use `{{cookiecutter.variable}}` placeholders:
```python
# In template file
"""{{cookiecutter.project_name}} - {{cookiecutter.project_short_description}}"""

def main():
    print("Hello from {{cookiecutter.project_slug}}!")
```

**Generated file** (after cookiecutter processes it):
```python
"""My Project - A data validation tool"""

def main():
    print("Hello from my_project!")
```

#### 4. Cookiecutter (Third-Party Tool)

**What it is**: Industry-standard project template engine

**What it does**:
- Clones template from Git
- Prompts for variables (or uses provided values)
- Processes template files (replaces `{{variables}}`)
- Generates project structure
- Runs hooks (pre/post generation scripts)

**Why we use it**:
- Battle-tested (used by thousands of projects)
- Supports Git repositories natively
- Handles complex templating logic
- Active community and ecosystem

### Data Flow: Step by Step

Let's trace what happens when you run the skill:

#### Step 1: User Input Collection

**Interactive Mode**:
```bash
$ python scripts/init_project.py --interactive

Project name: data-validator
CLI Framework:
  1. click
  2. typer
  3. argparse
Choose (1-3): 1
Integrations: files,api
```

**Non-Interactive Mode**:
```bash
$ python scripts/init_project.py \
    --name "data-validator" \
    --framework "click" \
    --integrations "files,api"
```

**Result**: Creates `ProjectRequirements` object:
```python
ProjectRequirements(
    name="data_validator",
    framework="click",
    integrations=["files", "api"],
    domain="A CLI application",
    author="Your Name",
    email="you@example.com"
)
```

#### Step 2: Template Selection

**Script loads** `template_sources.yaml`:
```python
templates = load_template_sources()
# Returns: {
#   "bdd-cli-click": TemplateConfig(...),
#   "bdd-cli-typer": TemplateConfig(...),
#   "bdd-cli-argparse": TemplateConfig(...)
# }
```

**Filters templates** by requirements:
```python
# 1. Filter by framework
candidates = [t for t in templates if t.framework == "click"]
# Result: [bdd-cli-click]

# 2. Check integration support
for integration in ["files", "api"]:
    candidates = [t for t in candidates
                  if integration in t.supports_integrations]
# Result: [bdd-cli-click]  (if it supports both)

# 3. Sort by priority
candidates.sort(key=lambda t: t.priority)

# 4. Select first (highest priority)
selected = candidates[0]
```

**Result**: Selected template with Git URL

#### Step 3: Template Fetching

**Builds cookiecutter command**:
```bash
cookiecutter gh:your-org/bdd-cli-click-template \
  --no-input \
  --output-dir /current/directory \
  project_name="data-validator" \
  project_slug="data_validator" \
  has_api_integration="yes" \
  has_files_integration="yes" \
  has_database_integration="no" \
  has_data_integration="no"
```

**Cookiecutter**:
1. Clones `gh:your-org/bdd-cli-click-template` from GitHub
2. Reads `cookiecutter.json`
3. Processes template files, replacing `{{variables}}`
4. Generates project in `./data_validator/`

#### Step 4: Post-Generation Setup

**Script runs**:
```bash
cd data_validator
git init
git add .
git commit -m "Initial commit from cookiecutter template"

uv venv
uv sync
uv run behave --dry-run  # Verify BDD tests structure
```

**Result**: Fully initialized project ready for development

#### Step 5: User Notification

**Script outputs**:
```
✓ Project generated: data_validator
✓ Post-setup complete!

Next Steps:
  1. cd data_validator
  2. source .venv/bin/activate
  3. uv run behave
  4. Review features/01_foundation.feature
```

---

## Installation & Setup

### Prerequisites

Before using this skill, you need:

#### Required Tools

1. **Python 3.11 or later**
   ```bash
   python --version
   # Should show: Python 3.11.x or higher
   ```

   **Install if needed**:
   - macOS: `brew install python@3.11`
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Linux: `sudo apt install python3.11` (Ubuntu/Debian)

2. **Git**
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

   **Install if needed**: [git-scm.com/downloads](https://git-scm.com/downloads)

3. **cookiecutter**
   ```bash
   cookiecutter --version
   # Should show: Cookiecutter 2.x.x
   ```

   **Install**:
   ```bash
   # Option 1: Using pip
   pip install cookiecutter

   # Option 2: Using uv (recommended)
   uv tool install cookiecutter

   # Option 3: Using pipx
   pipx install cookiecutter
   ```

4. **PyYAML** (Python library)
   ```bash
   pip install pyyaml
   ```

#### Recommended Tools

5. **uv** (fast Python package manager)
   ```bash
   uv --version
   ```

   **Install**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Why recommended**: Much faster than pip for installing dependencies in generated projects

### Verification

Run this verification script:

```bash
#!/bin/bash
echo "Checking prerequisites..."

python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python: $python_version"

git_version=$(git --version 2>&1 | awk '{print $3}')
echo "✓ Git: $git_version"

if command -v cookiecutter &> /dev/null; then
    cc_version=$(cookiecutter --version 2>&1)
    echo "✓ Cookiecutter: $cc_version"
else
    echo "✗ Cookiecutter: NOT INSTALLED"
fi

if command -v uv &> /dev/null; then
    uv_version=$(uv --version 2>&1)
    echo "✓ uv: $uv_version"
else
    echo "⚠ uv: NOT INSTALLED (recommended)"
fi

echo ""
echo "Ready to use init-project-cookiecutter!"
```

Save as `check_prereqs.sh`, run with `bash check_prereqs.sh`

### Getting the Skill

#### Option 1: Clone This Repository

```bash
git clone https://github.com/your-org/gherkin-expansion.git
cd gherkin-expansion/skills/init-project-cookiecutter
```

#### Option 2: Install as Claude Code Skill

```bash
# Copy to Claude Code skills directory
mkdir -p ~/.claude/skills
cp -r skills/init-project-cookiecutter ~/.claude/skills/

# Verify
ls ~/.claude/skills/init-project-cookiecutter
```

### Configuration

#### 1. Update Template Sources

Edit `scripts/template_sources.yaml` to point to **your actual template repositories**:

```yaml
templates:
  bdd-cli-click:
    name: "BDD CLI with Click Framework"
    git_url: "gh:YOUR-ORG/bdd-cli-click-template"  # ← Change this
    framework: "click"
    supports_integrations:
      - api
      - database
      - files
      - data
    priority: 1
    status: "stable"
```

**Replace**:
- `YOUR-ORG` with your GitHub organization/username
- Repository names with your actual template repos

#### 2. (Optional) Create User Override File

For personal templates, create:

**Location**: `~/.claude/template_sources_override.yaml`

**Content**:
```yaml
version: "2.0.0"

templates:
  my-personal-template:
    name: "My Custom BDD Template"
    git_url: "gh:myusername/my-bdd-template"
    framework: "click"
    supports_integrations:
      - api
    priority: 10
    status: "experimental"
```

This merges with the main configuration, with your overrides taking precedence.

---

## Quick Start Guide

### Your First Project (5 Minutes)

#### 1. Run Interactive Mode

```bash
cd skills/init-project-cookiecutter
python scripts/init_project.py --interactive
```

#### 2. Answer Questions

```
Project name: my-first-cli
  → Normalized to: my_first_cli

CLI Framework:
  1. click    - Full-featured, decorator-based (most popular)
  2. typer    - Modern, type-hint based (Click-powered)
  3. argparse - Standard library, minimal dependencies
  4. (skip)   - Let the system choose
Choose (1-4): 1

What does your tool do? (optional)
Domain: A simple hello world CLI

Integrations (comma-separated, or press Enter to skip):
  - api      : HTTP/REST API clients
  - database : Database operations
  - files    : File processing
  - data     : Data analysis
Integrations: [press Enter]

Author information (optional):
Your name: John Doe
Your email: john@example.com
```

#### 3. Watch It Generate

```
Selected template: BDD CLI with Click Framework
  Full-featured BDD-based CLI using Click

Fetching template from: gh:your-org/bdd-cli-click-template

Running post-generation setup...
  • Initializing git repository...
  • Creating virtual environment...
  • Installing dependencies...
  • Running initial tests...
  ✓ BDD tests structure verified

✓ Post-setup complete!
```

#### 4. Start Coding

```bash
cd my_first_cli
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Verify everything works
uv run behave --dry-run

# Run your CLI
my_first_cli hello
# Output: Hello from my_first_cli!
```

**Congratulations!** You have a working BDD CLI project.

---

## Detailed Usage

### Command-Line Interface

#### Basic Syntax

```bash
python scripts/init_project.py [OPTIONS]
```

#### Required Arguments (Pick One Mode)

**Interactive Mode**:
```bash
--interactive
```
Asks questions interactively. **Recommended for beginners**.

**OR**

**Non-Interactive Mode** (requires `--name`):
```bash
--name PROJECT_NAME
```
Generates project without prompting.

#### Optional Arguments

```bash
--framework {click,typer,argparse}
    CLI framework to use
    Example: --framework click

--domain DESCRIPTION
    What your tool does (one-line description)
    Example: --domain "Validates CSV data files"

--integrations LIST
    Comma-separated integrations
    Options: api, database, files, data
    Example: --integrations "api,files"

--author NAME
    Author name for pyproject.toml
    Default: "Your Name"
    Example: --author "Jane Doe"

--email EMAIL
    Author email for pyproject.toml
    Default: "you@example.com"
    Example: --email "jane@example.com"

--template-url URL
    Use specific template URL (bypasses selection)
    Example: --template-url "gh:org/custom-template"

--output-dir DIRECTORY
    Where to create project
    Default: current directory
    Example: --output-dir "/Users/name/projects"

--no-cache
    Skip cache, fetch fresh template from Git
    Default: uses cache if available

--list-templates
    List all available templates and exit
    Example: python scripts/init_project.py --list-templates
```

### Usage Modes

#### Mode 1: Interactive (Recommended)

**Best for**: Learning, exploring options, unsure about requirements

```bash
python scripts/init_project.py --interactive
```

**Pros**:
- Guides you through questions
- Explains options
- Validates input immediately
- No need to remember argument names

**Cons**:
- Can't script/automate
- Slower for repeated use

#### Mode 2: Non-Interactive

**Best for**: Automation, scripting, when you know exactly what you want

```bash
python scripts/init_project.py \
    --name "my-project" \
    --framework "click" \
    --domain "A data processing tool" \
    --integrations "files,data" \
    --author "Your Name" \
    --email "you@example.com"
```

**Pros**:
- Fast
- Scriptable
- Reproducible

**Cons**:
- Need to know argument names
- No guidance on options

#### Mode 3: List Templates

**Best for**: Seeing what's available before deciding

```bash
python scripts/init_project.py --list-templates
```

**Output**:
```
Available Templates (from Git repositories):

bdd-cli-click (priority: 1) [stable]
  Name: BDD CLI with Click Framework
  Repository: gh:your-org/bdd-cli-click-template
  Framework: click
  Integrations: api, database, files, data
  Description: Full-featured BDD-based CLI using Click

bdd-cli-typer (priority: 2) [stable]
  Name: BDD CLI with Typer Framework
  Repository: gl:your-group/bdd-cli-typer-template
  Framework: typer
  Integrations: api, database, files, data
  Description: Modern BDD-based CLI using Typer

[...]
```

#### Mode 4: Ad-Hoc Template URL

**Best for**: Testing new templates, using one-off templates

```bash
python scripts/init_project.py \
    --name "test-project" \
    --template-url "gh:someone/their-template"
```

Bypasses template selection, uses specified URL directly.

### Understanding Integrations

When you specify integrations, the generated project includes specific functionality:

#### `api` - HTTP/REST API Integration

**Adds**:
- `httpx` library (modern async HTTP client)
- `responses` library (for mocking API calls in tests)
- `infrastructure/api_client.py` module
- `features/04_api_integration.feature` BDD tests
- `steps/api_steps.py` step definitions

**Use when**: Your CLI makes HTTP requests to external APIs

**Example scenarios**:
- Fetching data from REST APIs
- Submitting data to web services
- Integrating with SaaS platforms (Stripe, GitHub, etc.)

#### `database` - Database Operations

**Adds**:
- `sqlalchemy` ORM library
- `psycopg2-binary` PostgreSQL driver
- `infrastructure/database.py` module
- `core/models.py` for ORM models
- `features/05_database_operations.feature` BDD tests
- `steps/database_steps.py` step definitions

**Use when**: Your CLI stores/queries data in databases

**Example scenarios**:
- Storing configuration in SQLite
- Querying PostgreSQL for reporting
- Managing database migrations

#### `files` - File Processing

**Adds**:
- `pypdf2` library (PDF processing)
- `python-magic-bin` (file type detection)
- `infrastructure/file_handler.py` module
- `features/03_file_operations.feature` BDD tests
- `steps/file_steps.py` step definitions

**Use when**: Your CLI processes files beyond simple text

**Example scenarios**:
- PDF manipulation
- Image processing
- Document format conversion
- File type detection

#### `data` - Data Analysis

**Adds**:
- `pandas` library (data manipulation)
- `numpy` library (numerical operations)
- `services/data_processor.py` module
- `features/06_data_processing.feature` BDD tests
- `steps/data_steps.py` step definitions

**Use when**: Your CLI analyzes or transforms data

**Example scenarios**:
- CSV data processing
- Statistical analysis
- Data aggregation and reporting
- Data transformation pipelines

#### Multiple Integrations

You can combine integrations:

```bash
# API client that caches results in database
--integrations "api,database"

# Data analysis tool that reads from files
--integrations "files,data"

# Complete application with all capabilities
--integrations "api,database,files,data"
```

### CLI Framework Comparison

#### Click (Priority 1)

**Best for**: Feature-rich CLIs with subcommands

**Code style**:
```python
import click

@click.group()
def cli():
    """My application."""
    pass

@cli.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello."""
    click.echo(f'Hello, {name}!')
```

**Pros**:
- Most popular (large community)
- Excellent documentation
- Rich option types (choices, multiple, etc.)
- Automatic help generation
- Plugin system

**Cons**:
- External dependency
- Decorator syntax may be unfamiliar

**Use when**: Building serious CLI tools with multiple commands

#### Typer (Priority 2)

**Best for**: Modern Python projects using type hints

**Code style**:
```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str = "World"):
    """Say hello."""
    typer.echo(f"Hello, {name}!")
```

**Pros**:
- Automatic validation from type hints
- Beautiful help messages (uses Rich)
- Simpler than Click
- FastAPI-style interface
- Built on Click (gets all Click benefits)

**Cons**:
- Newer (smaller community than Click)
- Requires Python 3.6+
- Less flexible for complex scenarios

**Use when**: You love type hints and want automatic validation

#### Argparse (Priority 3)

**Best for**: Minimal dependencies, maximum portability

**Code style**:
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='My application')
    parser.add_argument('--name', default='World', help='Name to greet')
    args = parser.parse_args()
    print(f'Hello, {args.name}!')
```

**Pros**:
- Standard library (no external dependencies)
- Maximum compatibility
- Well-documented
- Simple and straightforward

**Cons**:
- More verbose than Click/Typer
- Manual help formatting
- Limited built-in validation
- No automatic type conversion

**Use when**: Dependencies must be minimal or you want stdlib-only

### Project Naming Conventions

#### Valid Project Names

Must follow Python package naming rules:

**✅ Valid**:
- `my-project` (converted to `my_project`)
- `data_validator`
- `api-client-v2`
- `loganalyzer`

**❌ Invalid**:
- `2data` (starts with number)
- `my project` (space, converted to underscore)
- `my-project!` (special character)
- `class` (Python keyword)

#### Name Normalization

The script automatically normalizes names:

| Input | Normalized Output |
|-------|------------------|
| `my-project` | `my_project` |
| `My Project` | `my_project` |
| `MyProject` | `myproject` |
| `my_project` | `my_project` |

---

## Understanding Templates

### What Is a Cookiecutter Template?

A cookiecutter template is a **parameterized project structure** stored in a Git repository.

#### Anatomy of a Template

```
template-repository/
│
├── cookiecutter.json              # ← Template variables/parameters
│
├── hooks/                         # ← Optional scripts
│   ├── pre_gen_project.py        #    Run before generation
│   └── post_gen_project.py       #    Run after generation
│
└── {{cookiecutter.project_slug}}/ # ← The actual project template
    ├── src/
    │   └── {{cookiecutter.project_slug}}/
    │       ├── __init__.py
    │       ├── core/
    │       ├── infrastructure/
    │       ├── services/
    │       └── cli/
    │           └── main.py        # ← Uses {{variables}}
    ├── tests/
    │   ├── unit/
    │   └── integration/
    ├── features/
    │   ├── environment.py
    │   ├── behave.ini
    │   └── 01_foundation.feature
    ├── pyproject.toml             # ← Uses {{variables}}
    ├── README.md                  # ← Uses {{variables}}
    └── .gitignore
```

### Template Variables

#### `cookiecutter.json` Example

```json
{
  "project_name": "My Project",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "project_short_description": "A BDD-based CLI application",
  "cli_framework": "click",
  "has_api_integration": ["yes", "no"],
  "has_database_integration": ["yes", "no"],
  "has_files_integration": ["yes", "no"],
  "has_data_integration": ["yes", "no"],
  "author_name": "Your Name",
  "author_email": "you@example.com",
  "python_version": "3.11",
  "license": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"]
}
```

#### Variable Types

**Simple variables**:
```json
"project_name": "My Project"
```

**Computed variables** (use Jinja2 templating):
```json
"project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_') }}"
```

**Choice variables** (list of options):
```json
"license": ["MIT", "Apache-2.0", "GPL-3.0"]
```

#### Using Variables in Templates

**Template file** (`pyproject.toml.template`):
```toml
[project]
name = "{{cookiecutter.project_slug}}"
version = "0.1.0"
description = "{{cookiecutter.project_short_description}}"
authors = [
    {name = "{{cookiecutter.author_name}}", email = "{{cookiecutter.author_email}}"},
]
```

**Generated file** (after cookiecutter processes it):
```toml
[project]
name = "my_project"
version = "0.1.0"
description = "A data validation tool"
authors = [
    {name = "John Doe", email = "john@example.com"},
]
```

### Hooks Explained

Hooks are Python scripts that run during template generation.

#### Pre-Generation Hook

**File**: `hooks/pre_gen_project.py`

**Purpose**: Validate inputs before generating files

**Example**:
```python
"""Validate project configuration."""
import re
import sys

project_slug = "{{ cookiecutter.project_slug }}"

# Validate project name
if not re.match(r'^[a-z][a-z0-9_]*$', project_slug):
    print(f"Error: Invalid project_slug '{project_slug}'")
    print("Must start with letter, contain only lowercase letters, numbers, underscores")
    sys.exit(1)

# Check Python keyword
import keyword
if keyword.iskeyword(project_slug):
    print(f"Error: '{project_slug}' is a Python keyword")
    sys.exit(1)

print(f"✓ Generating project: {project_slug}")
```

#### Post-Generation Hook

**File**: `hooks/post_gen_project.py`

**Purpose**: Set up project after files are generated

**Example**:
```python
"""Setup project after generation."""
import subprocess
import sys
from pathlib import Path

project_root = Path.cwd()

# Remove files based on integration flags
has_api = "{{ cookiecutter.has_api_integration }}" == "yes"
has_database = "{{ cookiecutter.has_database_integration }}" == "yes"

if not has_api:
    api_file = project_root / "src" / "{{ cookiecutter.project_slug }}" / "infrastructure" / "api_client.py"
    if api_file.exists():
        api_file.unlink()
        print("  Removed: api_client.py (not needed)")

if not has_database:
    db_file = project_root / "src" / "{{ cookiecutter.project_slug }}" / "infrastructure" / "database.py"
    if db_file.exists():
        db_file.unlink()
        print("  Removed: database.py (not needed)")

# Initialize git repository
print("\n  Initializing git...")
subprocess.run(["git", "init"], capture_output=True, check=True)
subprocess.run(["git", "add", "."], capture_output=True, check=True)

print("\n✓ Project ready!")
print("\nNext steps:")
print("  1. cd {{ cookiecutter.project_slug }}")
print("  2. uv venv && source .venv/bin/activate")
print("  3. uv sync")
print("  4. uv run behave")
```

### Template Repository Patterns

Templates can be organized in different ways:

#### Pattern 1: Dedicated Repository

**One template per repository**

```
github.com/your-org/bdd-cli-click-template/
├── cookiecutter.json
├── hooks/
└── {{cookiecutter.project_slug}}/
```

**Configuration**:
```yaml
templates:
  bdd-cli-click:
    git_url: "gh:your-org/bdd-cli-click-template"
```

**Pros**:
- Simple structure
- Easy to maintain
- Clear versioning

**Cons**:
- Many repositories if many templates

#### Pattern 2: Monorepo with Subdirectories

**Multiple templates in one repository**

```
github.com/your-org/python-templates/
├── cli-templates/
│   ├── bdd-click/
│   │   ├── cookiecutter.json
│   │   └── {{cookiecutter.project_slug}}/
│   ├── bdd-typer/
│   │   ├── cookiecutter.json
│   │   └── {{cookiecutter.project_slug}}/
│   └── bdd-argparse/
│       ├── cookiecutter.json
│       └── {{cookiecutter.project_slug}}/
└── README.md
```

**Configuration**:
```yaml
templates:
  bdd-cli-click:
    git_url: "gh:your-org/python-templates"
    directory: "cli-templates/bdd-click"

  bdd-cli-typer:
    git_url: "gh:your-org/python-templates"
    directory: "cli-templates/bdd-typer"
```

**Pros**:
- Fewer repositories
- Related templates together
- Shared documentation

**Cons**:
- Larger repository
- More complex structure

#### Pattern 3: Versioned with Branches/Tags

**Use Git features for versions**

```
github.com/your-org/bdd-cli-template/
  Branches:
    - main (latest stable)
    - develop (bleeding edge)
    - legacy-v1 (old version)
  Tags:
    - v1.0.0
    - v2.0.0
    - v2.1.0
    - v2.2.0
```

**Configuration**:
```yaml
templates:
  bdd-cli-latest:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "main"

  bdd-cli-stable:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "v2.0.0"

  bdd-cli-dev:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "develop"

  bdd-cli-legacy:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "v1.0.0"
```

**Pros**:
- Native version control
- Easy to reference specific versions
- Can maintain old versions

**Cons**:
- Need to manage branches/tags
- Breaking changes affect all versions

---

## Template Management

### Adding New Templates

#### Step 1: Create Template Repository

```bash
# Create new directory
mkdir my-bdd-template
cd my-bdd-template

# Create structure
mkdir -p hooks
mkdir -p "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}"
```

#### Step 2: Create `cookiecutter.json`

```json
{
  "project_name": "My Project",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "project_short_description": "A BDD-based CLI application",
  "cli_framework": "click",
  "has_api_integration": "no",
  "has_database_integration": "no",
  "has_files_integration": "no",
  "has_data_integration": "no",
  "author_name": "Your Name",
  "author_email": "you@example.com",
  "python_version": "3.11",
  "license": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"]
}
```

#### Step 3: Create Project Structure

```bash
cd "{{cookiecutter.project_slug}}"

# Create directories
mkdir -p src/{{cookiecutter.project_slug}}/{core,infrastructure,services,cli,config}
mkdir -p tests/{unit,integration}
mkdir -p features/steps

# Create files (examples below)
```

**Example**: `pyproject.toml`
```toml
[project]
name = "{{cookiecutter.project_slug}}"
version = "0.1.0"
description = "{{cookiecutter.project_short_description}}"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "structlog>=24.0",
    "rich>=13.0",
    {% if cookiecutter.cli_framework == "click" %}
    "click>=8.1",
    {% elif cookiecutter.cli_framework == "typer" %}
    "typer>=0.12",
    {% endif %}
    {% if cookiecutter.has_api_integration == "yes" %}
    "httpx>=0.27",
    {% endif %}
    {% if cookiecutter.has_database_integration == "yes" %}
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9",
    {% endif %}
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "mypy>=1.8",
    "ruff>=0.6",
    "behave>=1.2.6",
    {% if cookiecutter.has_api_integration == "yes" %}
    "responses>=0.25",
    {% endif %}
]
```

**Example**: `src/{{cookiecutter.project_slug}}/cli/main.py`
```python
"""{{cookiecutter.project_name}} - {{cookiecutter.project_short_description}}"""
{% if cookiecutter.cli_framework == "click" %}
import click

@click.group()
def cli():
    """{{cookiecutter.project_name}}"""
    pass

@cli.command()
def hello():
    """Say hello."""
    click.echo("Hello from {{cookiecutter.project_slug}}!")

if __name__ == "__main__":
    cli()
{% elif cookiecutter.cli_framework == "typer" %}
import typer

app = typer.Typer()

@app.command()
def hello():
    """Say hello."""
    typer.echo("Hello from {{cookiecutter.project_slug}}!")

def cli():
    app()

if __name__ == "__main__":
    cli()
{% endif %}
```

#### Step 4: Add Hooks (Optional)

**`hooks/pre_gen_project.py`**:
```python
"""Validate before generation."""
import re
import sys

slug = "{{ cookiecutter.project_slug }}"
if not re.match(r'^[a-z][a-z0-9_]*$', slug):
    print(f"Error: Invalid project_slug '{slug}'")
    sys.exit(1)

print(f"✓ Generating: {slug}")
```

**`hooks/post_gen_project.py`**:
```python
"""Setup after generation."""
from pathlib import Path

# Remove unused files
if "{{ cookiecutter.has_api_integration }}" != "yes":
    api_file = Path("src/{{ cookiecutter.project_slug }}/infrastructure/api_client.py")
    if api_file.exists():
        api_file.unlink()

print("\n✓ Project ready!")
```

#### Step 5: Test Locally

```bash
# Test template generation
cd /tmp
cookiecutter /path/to/my-bdd-template --no-input

# Verify generated project
cd my_project
ls -la
```

#### Step 6: Push to Git

```bash
cd /path/to/my-bdd-template

git init
git add .
git commit -m "Initial template"
git remote add origin git@github.com:your-org/my-bdd-template.git
git push -u origin main

# Optional: Create version tag
git tag v1.0.0
git push --tags
```

#### Step 7: Register Template

Edit `scripts/template_sources.yaml`:

```yaml
templates:
  # ... existing templates ...

  my-custom-bdd:
    name: "My Custom BDD Template"
    description: "Custom BDD template with special features"
    git_url: "gh:your-org/my-bdd-template"
    framework: "click"
    supports_integrations:
      - api
      - files
    priority: 10  # Higher number = lower priority
    status: "experimental"
```

#### Step 8: Test with Skill

```bash
cd skills/init-project-cookiecutter

# Test template
python scripts/init_project.py \
    --name "test-project" \
    --template-url "gh:your-org/my-bdd-template"

# Verify
cd test-project
uv run behave --dry-run
```

### Updating Existing Templates

#### Using Git Branches

**Scenario**: You want to add a new feature to a template without breaking existing users.

**Solution**: Use branches

```bash
cd my-bdd-template

# Create feature branch
git checkout -b feature/add-logging

# Make changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Add logging support"
git push -u origin feature/add-logging
```

**Register branch**:
```yaml
templates:
  my-custom-bdd-dev:
    git_url: "gh:your-org/my-bdd-template"
    checkout: "feature/add-logging"
    status: "experimental"
```

#### Using Git Tags (Recommended)

**Scenario**: Release stable versions of templates

```bash
cd my-bdd-template

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "Version 2.0: Add new features"

# Tag version
git tag v2.0.0
git push && git push --tags
```

**Register versions**:
```yaml
templates:
  my-custom-bdd-stable:
    git_url: "gh:your-org/my-bdd-template"
    checkout: "v1.0.0"
    status: "stable"

  my-custom-bdd-latest:
    git_url: "gh:your-org/my-bdd-template"
    checkout: "v2.0.0"
    status: "stable"

  my-custom-bdd-dev:
    git_url: "gh:your-org/my-bdd-template"
    checkout: "main"
    status: "beta"
```

### Removing Templates

#### From Registry

Edit `template_sources.yaml` and delete the template entry.

**Before**:
```yaml
templates:
  old-template:
    git_url: "gh:org/old-template"
    framework: "click"

  current-template:
    git_url: "gh:org/current-template"
    framework: "click"
```

**After**:
```yaml
templates:
  current-template:
    git_url: "gh:org/current-template"
    framework: "click"
```

#### Deprecating (Recommended)

Instead of removing, mark as deprecated:

```yaml
templates:
  old-template:
    git_url: "gh:org/old-template"
    framework: "click"
    status: "deprecated"
    priority: 999  # Very low priority
```

### Caching

#### How Caching Works

1. **First fetch**: Template cloned to `~/.claude/cookiecutter_cache/<template-id>/`
2. **Subsequent fetches**: Uses cached copy if fresh (< 7 days)
3. **Cache refresh**: Auto-updates if expired
4. **Manual refresh**: Use `--no-cache` flag

#### Cache Configuration

In `template_sources.yaml`:

```yaml
cache:
  enabled: true
  location: "~/.claude/cookiecutter_cache"
  ttl_days: 7  # Re-clone after 7 days
  auto_clean: true
```

#### Managing Cache

**Clear all cache**:
```bash
rm -rf ~/.claude/cookiecutter_cache
```

**Clear specific template**:
```bash
rm -rf ~/.claude/cookiecutter_cache/bdd-cli-click
```

**Disable cache for one run**:
```bash
python scripts/init_project.py --no-cache --name "my-project"
```

---

## Advanced Usage

### Custom Template URLs

Use templates not in your registry:

```bash
# GitHub
python scripts/init_project.py \
    --name "test" \
    --template-url "gh:other-org/their-template"

# GitLab
python scripts/init_project.py \
    --name "test" \
    --template-url "gl:group/template"

# Full HTTPS URL
python scripts/init_project.py \
    --name "test" \
    --template-url "https://git.example.com/templates/bdd.git"

# With subdirectory
python scripts/init_project.py \
    --name "test" \
    --template-url "gh:org/monorepo --directory templates/cli"

# With specific version
python scripts/init_project.py \
    --name "test" \
    --template-url "gh:org/template --checkout v2.0.0"
```

### Scripting & Automation

#### Batch Project Creation

```bash
#!/bin/bash
# create_projects.sh

projects=(
  "data-validator:click:files"
  "api-client:typer:api,database"
  "log-analyzer:argparse:files,data"
)

for project in "${projects[@]}"; do
  IFS=':' read -r name framework integrations <<< "$project"

  echo "Creating $name..."
  python scripts/init_project.py \
    --name "$name" \
    --framework "$framework" \
    --integrations "$integrations" \
    --author "DevOps Team" \
    --email "devops@example.com"
done
```

#### CI/CD Integration

```yaml
# .github/workflows/scaffold-project.yml
name: Scaffold New Project

on:
  workflow_dispatch:
    inputs:
      project_name:
        description: 'Project name'
        required: true
      framework:
        description: 'CLI framework'
        required: true
        type: choice
        options:
          - click
          - typer
          - argparse
      integrations:
        description: 'Integrations (comma-separated)'
        required: false

jobs:
  scaffold:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install cookiecutter pyyaml

      - name: Generate project
        run: |
          cd skills/init-project-cookiecutter
          python scripts/init_project.py \
            --name "${{ github.event.inputs.project_name }}" \
            --framework "${{ github.event.inputs.framework }}" \
            --integrations "${{ github.event.inputs.integrations }}"

      - name: Create repository
        run: |
          # Create new repo and push generated project
          # (implementation depends on your Git platform)
```

### Environment Variables

Set default values via environment:

```bash
export COOKIECUTTER_AUTHOR_NAME="Jane Doe"
export COOKIECUTTER_AUTHOR_EMAIL="jane@example.com"
export COOKIECUTTER_DEFAULT_FRAMEWORK="click"

python scripts/init_project.py --interactive
# Will use these as defaults
```

### Template Testing

#### Test Template Locally Before Pushing

```bash
# Test from local directory
cookiecutter /path/to/template --no-input

# Test specific variable values
cookiecutter /path/to/template --no-input \
  project_name="Test Project" \
  has_api_integration="yes"

# Test interactively (asks for variables)
cookiecutter /path/to/template
```

#### Automated Template Testing

```python
# test_template.py
import subprocess
import tempfile
from pathlib import Path

def test_template_generation():
    """Test that template generates successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate project
        result = subprocess.run([
            "cookiecutter",
            "gh:org/template",
            "--no-input",
            "--output-dir", tmpdir,
            "project_name=test_project"
        ], capture_output=True)

        assert result.returncode == 0

        # Verify files exist
        project_dir = Path(tmpdir) / "test_project"
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()

def test_generated_project_works():
    """Test that generated project's tests pass."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate
        subprocess.run([
            "cookiecutter",
            "gh:org/template",
            "--no-input",
            "--output-dir", tmpdir
        ])

        project_dir = Path(tmpdir) / "my_project"

        # Install and test
        subprocess.run(["uv", "venv"], cwd=project_dir, check=True)
        subprocess.run(["uv", "sync"], cwd=project_dir, check=True)
        result = subprocess.run(
            ["uv", "run", "behave", "--dry-run"],
            cwd=project_dir,
            capture_output=True
        )

        assert result.returncode == 0
```

---

## Troubleshooting

### Common Issues

#### Issue: "cookiecutter: command not found"

**Symptoms**:
```
bash: cookiecutter: command not found
```

**Cause**: Cookiecutter not installed

**Solution**:
```bash
# Try one of these:
pip install cookiecutter
uv tool install cookiecutter
pipx install cookiecutter

# Verify
cookiecutter --version
```

#### Issue: "PyYAML module not found"

**Symptoms**:
```
ModuleNotFoundError: No module named 'yaml'
```

**Cause**: PyYAML library not installed

**Solution**:
```bash
pip install pyyaml

# Verify
python -c "import yaml; print('OK')"
```

#### Issue: Git Clone Fails

**Symptoms**:
```
GitCloneError: Failed to clone template repository
fatal: could not read Username for 'https://github.com'
```

**Cause**: SSH keys not configured or repository private

**Solution**:

**Option 1**: Use HTTPS with token
```yaml
# In template_sources.yaml
git_url: "https://YOUR-TOKEN@github.com/org/repo.git"
```

**Option 2**: Set up SSH keys
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and add to GitHub Settings → SSH Keys

# Test
ssh -T git@github.com
```

**Option 3**: Use HTTPS URL
```yaml
git_url: "https://github.com/org/repo.git"
```

#### Issue: Template Not Found

**Symptoms**:
```
TemplateNotFoundError: No template found for framework=click, integrations=['data']
```

**Cause**: No template supports requested combination

**Solution**:

1. **List available templates**:
   ```bash
   python scripts/init_project.py --list-templates
   ```

2. **Check what integrations are supported**

3. **Options**:
   - Remove unsupported integration
   - Choose different framework
   - Add template that supports combination
   - Use ad-hoc template URL

#### Issue: Integration Not Supported

**Symptoms**:
```
IntegrationNotSupportedError: No template supports all requested integrations: database, data
```

**Cause**: No template has both integrations

**Solution**:

Check template registry:
```yaml
templates:
  bdd-cli-click:
    supports_integrations:
      - api
      - database
      - files
      # Missing: data
```

**Fix**: Either:
- Remove `data` integration from request
- Update template to support `data`
- Use different template

#### Issue: Permission Denied

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: '/Users/name/.claude/cookiecutter_cache'
```

**Cause**: Cache directory not writable

**Solution**:
```bash
# Fix permissions
chmod -R u+w ~/.claude/cookiecutter_cache

# Or delete and recreate
rm -rf ~/.claude/cookiecutter_cache
mkdir -p ~/.claude/cookiecutter_cache
```

#### Issue: Project Already Exists

**Symptoms**:
```
FileExistsError: Directory 'my_project' already exists
```

**Cause**: Project with same name exists

**Solution**:
```bash
# Option 1: Choose different name
python scripts/init_project.py --name "my-project-v2"

# Option 2: Remove existing (careful!)
rm -rf my_project

# Option 3: Move existing
mv my_project my_project.old
```

#### Issue: Python Version Too Old

**Symptoms**:
```
PrerequisiteError: Python 3.11+ is required, but you have 3.9
```

**Cause**: Python version < 3.11

**Solution**:
```bash
# macOS with Homebrew
brew install python@3.11
brew link python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Verify
python3.11 --version
```

#### Issue: Generated Project Tests Fail

**Symptoms**:
After generation, running `uv run behave` fails

**Causes & Solutions**:

**Cause 1**: Virtual environment not activated
```bash
# Activate first
source .venv/bin/activate
behave
```

**Cause 2**: Dependencies not installed
```bash
uv sync
uv run behave
```

**Cause 3**: Template issue
```bash
# Test template independently
cookiecutter gh:org/template --no-input
cd my_project
uv venv && uv sync
uv run behave --dry-run
# If fails, template needs fixing
```

### Debugging Tips

#### Enable Verbose Output

```bash
# Cookiecutter verbose mode
python scripts/init_project.py --name "test" 2>&1 | tee debug.log

# Check what cookiecutter is doing
cookiecutter gh:org/template --verbose
```

#### Test Template Directly

Bypass the skill script:

```bash
# Test cookiecutter directly
cookiecutter gh:your-org/template \
  --no-input \
  project_name="test_project" \
  has_api_integration="yes"

# If works: Problem is in skill script
# If fails: Problem is in template
```

#### Check YAML Syntax

```bash
# Validate template_sources.yaml
python -c "import yaml; yaml.safe_load(open('scripts/template_sources.yaml'))"

# If error: Fix YAML syntax
```

#### Inspect Cache

```bash
# See cached templates
ls -la ~/.claude/cookiecutter_cache/

# Check template cache
ls -la ~/.claude/cookiecutter_cache/bdd-cli-click/

# Clear specific cache
rm -rf ~/.claude/cookiecutter_cache/bdd-cli-click
```

---

## Best Practices

### For Template Users

#### 1. Pin Template Versions

**Bad**:
```yaml
git_url: "gh:org/template"  # Uses latest, could break
```

**Good**:
```yaml
git_url: "gh:org/template"
checkout: "v2.0.0"  # Pinned version, stable
```

#### 2. Test Generated Projects

After generation:
```bash
cd my_project

# Run all checks
uv run ruff check .
uv run mypy src/
uv run pytest
uv run behave

# If all pass, you're good to go
```

#### 3. Review Generated Code

Don't blindly trust templates. Review:
- Dependencies in `pyproject.toml`
- Security settings
- Default configurations
- Generated tests

#### 4. Customize After Generation

Templates are starting points, not final products:
```bash
# After generation
cd my_project

# Customize for your needs
vim pyproject.toml  # Add dependencies
vim README.md       # Update documentation
vim features/       # Modify BDD scenarios
```

#### 5. Keep Templates Updated

```bash
# Periodically refresh cache
python scripts/init_project.py --no-cache --name "test"

# Or clear cache
rm -rf ~/.claude/cookiecutter_cache
```

### For Template Authors

#### 1. Version Your Templates

Use semantic versioning:
```bash
git tag v1.0.0  # Initial release
git tag v1.1.0  # Minor update (new features)
git tag v2.0.0  # Major update (breaking changes)
```

#### 2. Document Variables

In `cookiecutter.json`, add comments (JSON doesn't support, use README):

**README.md** in template repo:
```markdown
## Template Variables

- `project_name`: Human-readable name (e.g., "My Project")
- `project_slug`: Python package name (auto-generated from project_name)
- `has_api_integration`: "yes" or "no" - Include API client code
- `has_database_integration`: "yes" or "no" - Include database code
```

#### 3. Test Generated Projects

```bash
# Test that generation works
cookiecutter . --no-input

# Test that generated project works
cd my_project
uv venv && uv sync
uv run pytest
uv run behave
```

#### 4. Use Hooks Wisely

**Pre-gen hook** for validation:
```python
# hooks/pre_gen_project.py
"""Validate inputs."""
import sys

# Validate
if invalid:
    print("Error: ...")
    sys.exit(1)
```

**Post-gen hook** for cleanup:
```python
# hooks/post_gen_project.py
"""Remove unused files."""
from pathlib import Path

if "{{ cookiecutter.has_api_integration }}" != "yes":
    Path("src/.../api_client.py").unlink()
```

#### 5. Provide Examples

Include example code in templates:
```python
# src/{{cookiecutter.project_slug}}/cli/main.py

"""{{cookiecutter.project_name}}

Example usage:
    $ {{cookiecutter.project_slug}} hello
    $ {{cookiecutter.project_slug}} process --input data.csv
"""
```

#### 6. Keep Dependencies Minimal

Only include essential dependencies:
```toml
dependencies = [
    "pydantic>=2.0",  # Essential for data validation
    "rich>=13.0",     # Essential for CLI output
]

[project.optional-dependencies]
extra = [
    "pandas>=2.0",  # Optional, only if needed
]
```

### For Template Managers

#### 1. Organize Templates Logically

```yaml
templates:
  # Core templates (priority 1-10)
  bdd-cli-click:
    priority: 1

  bdd-cli-typer:
    priority: 2

  # Specialized templates (priority 11-20)
  bdd-cli-click-api-heavy:
    priority: 11

  # Experimental templates (priority 90+)
  bdd-cli-experimental:
    priority: 90
    status: "experimental"
```

#### 2. Deprecate Gradually

```yaml
templates:
  old-template:
    status: "deprecated"
    priority: 999
    deprecation_message: "Use 'new-template' instead"

  new-template:
    status: "stable"
    priority: 1
```

#### 3. Document Template Differences

In main README or template_sources.yaml:
```yaml
templates:
  bdd-cli-click:
    description: "Standard Click template with all integrations"
    use_when: "Building general-purpose CLI"

  bdd-cli-click-minimal:
    description: "Minimal Click template, no integrations"
    use_when: "Simple CLI, minimal dependencies"
```

#### 4. Regular Audits

Quarterly review:
- Remove truly deprecated templates
- Update dependencies in templates
- Check for security issues
- Test all templates still work

---

## FAQ

### General Questions

**Q: Do I need to create templates myself?**

A: No. You can use existing templates from:
- Your organization's template repositories
- Public cookiecutter templates (adapt for BDD)
- This project's example templates (once created)

**Q: Can I use this without Git?**

A: No, templates must be in Git repositories. Cookiecutter requires Git to fetch templates.

**Q: Does this work on Windows?**

A: Yes, but:
- Use `.\venv\Scripts\activate` (not `source .venv/bin/activate`)
- Some paths may need adjustment
- Git Bash recommended over CMD

**Q: Can I use this in CI/CD?**

A: Yes! Use non-interactive mode:
```bash
python scripts/init_project.py \
  --name "$PROJECT_NAME" \
  --framework "$FRAMEWORK"
```

### Template Questions

**Q: Can templates be private repositories?**

A: Yes, if you have access:
- SSH: Configure SSH keys
- HTTPS: Use token in URL: `https://TOKEN@github.com/org/repo.git`

**Q: How do I update a template?**

A: Push changes to Git:
```bash
cd template-repo
# make changes
git commit -m "Update"
git push
```

Users get updates automatically (unless they pinned to specific version).

**Q: Can I have templates in different Git platforms?**

A: Yes! Supported:
- GitHub: `gh:org/repo`
- GitLab: `gl:org/repo`
- Bitbucket: `bb:org/repo`
- Any Git server: `https://git.example.com/repo.git`

**Q: What if a template is broken?**

A: Options:
1. Pin to known-good version: `checkout: "v1.0.0"`
2. Fork template and fix
3. Report issue to template maintainer
4. Use different template

### Usage Questions

**Q: Can I modify generated projects?**

A: Yes! Generated projects are yours to modify. Templates are just starting points.

**Q: Will updating the template affect my project?**

A: No. Once generated, your project is independent. Template updates don't affect it.

**Q: Can I use custom CLI frameworks (not Click/Typer/argparse)?**

A: Yes, create a custom template with your framework.

**Q: How do I share templates with my team?**

A: Two options:
1. Push template to shared Git repo
2. Add to team's `template_sources.yaml`:
   ```yaml
   templates:
     team-template:
       git_url: "gh:your-org/team-template"
   ```

### Troubleshooting Questions

**Q: Why is template generation slow?**

A: Possible causes:
- First fetch (cloning from Git)
- Slow network connection
- Large template repository

**Solution**: Use caching (default behavior)

**Q: Can I see what cookiecutter is doing?**

A: Yes, add verbose flag:
```bash
cookiecutter gh:org/template --verbose
```

**Q: How do I report issues?**

A: Depends on issue:
- Skill script issue: Report to this project
- Template issue: Report to template repo
- Cookiecutter issue: Report to cookiecutter project

---

## Examples & Recipes

### Example 1: Simple Hello World CLI

**Goal**: Create minimal CLI that says hello

**Command**:
```bash
python scripts/init_project.py \
  --name "hello-cli" \
  --framework "click" \
  --domain "A simple greeting CLI"
```

**Generated structure**:
```
hello_cli/
├── src/hello_cli/
│   └── cli/
│       └── main.py
├── tests/
├── features/
└── pyproject.toml
```

**Usage**:
```bash
cd hello_cli
source .venv/bin/activate
hello-cli hello
# Output: Hello from hello_cli!
```

### Example 2: Data Validation Tool

**Goal**: CLI to validate CSV files

**Command**:
```bash
python scripts/init_project.py \
  --name "data-validator" \
  --framework "click" \
  --domain "Validates CSV data against schemas" \
  --integrations "files"
```

**What you get**:
- CSV file handling code
- File processing utilities
- BDD tests for file operations

**Next steps**:
```bash
cd data_validator

# Add your validation logic
vim src/data_validator/services/validator.py

# Write BDD scenarios
vim features/02_validation.feature

# Implement and test
uv run behave --tags=@wip
```

### Example 3: API Client with Database Caching

**Goal**: CLI to fetch from API and cache in database

**Command**:
```bash
python scripts/init_project.py \
  --name "api-client" \
  --framework "typer" \
  --domain "REST API client with database caching" \
  --integrations "api,database"
```

**What you get**:
- HTTP client setup (httpx)
- Database models (SQLAlchemy)
- API mocking for tests
- BDD scenarios for both API and DB

**Generated code includes**:
```
api_client/
├── src/api_client/
│   ├── infrastructure/
│   │   ├── api_client.py     # HTTP client
│   │   └── database.py       # DB connection
│   ├── core/
│   │   └── models.py         # ORM models
│   └── services/
│       └── cache_service.py  # Caching logic
├── features/
│   ├── 04_api_integration.feature
│   └── 05_database_operations.feature
```

### Example 4: Log Analyzer

**Goal**: Parse and analyze log files

**Command**:
```bash
python scripts/init_project.py \
  --name "log-analyzer" \
  --framework "argparse" \
  --domain "Analyzes log files for patterns and anomalies" \
  --integrations "files,data"
```

**What you get**:
- File reading utilities
- Data processing with pandas
- Minimal dependencies (argparse is stdlib)

**Use case**:
```bash
cd log_analyzer
source .venv/bin/activate

# Your CLI usage
log-analyzer parse --file app.log
log-analyzer analyze --file app.log --pattern "ERROR"
log-analyzer report --file app.log --output report.csv
```

### Recipe: Testing a New Template

**Goal**: Test template before using in production

**Steps**:

1. **Test generation**:
   ```bash
   python scripts/init_project.py \
     --name "test-project" \
     --template-url "gh:org/new-template"
   ```

2. **Verify structure**:
   ```bash
   cd test_project
   tree -L 3
   ```

3. **Check dependencies**:
   ```bash
   cat pyproject.toml
   ```

4. **Test installation**:
   ```bash
   uv venv && uv sync
   ```

5. **Run tests**:
   ```bash
   uv run pytest
   uv run behave
   ```

6. **Test CLI**:
   ```bash
   uv run python -m test_project --help
   ```

7. **Clean up**:
   ```bash
   cd ..
   rm -rf test_project
   ```

### Recipe: Batch Creating Similar Projects

**Goal**: Create multiple similar projects

**Script** (`batch_create.sh`):
```bash
#!/bin/bash

PROJECTS=(
  "service-a:api,database"
  "service-b:api,database"
  "service-c:api,database"
)

FRAMEWORK="typer"
BASE_DOMAIN="Microservice for"

for project in "${PROJECTS[@]}"; do
  IFS=':' read -r name integrations <<< "$project"

  echo "Creating $name..."

  python scripts/init_project.py \
    --name "$name" \
    --framework "$FRAMEWORK" \
    --domain "$BASE_DOMAIN $name" \
    --integrations "$integrations" \
    --author "DevOps Team" \
    --email "devops@example.com"

  echo "✓ Created $name"
  echo ""
done

echo "All projects created!"
```

**Usage**:
```bash
chmod +x batch_create.sh
./batch_create.sh
```

### Recipe: Custom Template for Your Organization

**Goal**: Create standardized template for your team

**Steps**:

1. **Create template from successful project**:
   ```bash
   # Take a project that works well
   cd successful_project

   # Convert to template
   # Replace specific values with {{variables}}
   ```

2. **Create `cookiecutter.json`**:
   ```json
   {
     "project_name": "Company Project",
     "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_') }}",
     "company": "YourCompany",
     "team": "Engineering",
     "compliance_level": ["standard", "high", "critical"]
   }
   ```

3. **Add company-specific boilerplate**:
   ```python
   # src/{{cookiecutter.project_slug}}/config/company.py
   """{{cookiecutter.company}} standard configuration."""

   COMPANY = "{{cookiecutter.company}}"
   TEAM = "{{cookiecutter.team}}"
   COMPLIANCE = "{{cookiecutter.compliance_level}}"
   ```

4. **Push to company Git**:
   ```bash
   git remote add origin git@github.com:your-company/bdd-template.git
   git push -u origin main
   ```

5. **Register in team config**:
   ```yaml
   # ~/.claude/template_sources_override.yaml
   templates:
     company-standard:
       git_url: "gh:your-company/bdd-template"
       framework: "click"
   ```

6. **Use company-wide**:
   ```bash
   python scripts/init_project.py \
     --name "new-service" \
     --template-url "gh:your-company/bdd-template"
   ```

---

## Reference

### Command-Line Reference

```
usage: init_project.py [-h] [--interactive] [--list-templates] [--name NAME]
                       [--framework {click,typer,argparse}] [--domain DOMAIN]
                       [--integrations INTEGRATIONS] [--author AUTHOR]
                       [--email EMAIL] [--template-url TEMPLATE_URL]
                       [--output-dir OUTPUT_DIR] [--no-cache]

Initialize BDD CLI project from Git-based cookiecutter template

optional arguments:
  -h, --help            show this help message and exit
  --interactive         Interactive mode (ask user for requirements)
  --list-templates      List available templates and exit
  --name NAME           Project name
  --framework {click,typer,argparse}
                        CLI framework
  --domain DOMAIN       Project domain/description
  --integrations INTEGRATIONS
                        Comma-separated integrations (api,database,files,data)
  --author AUTHOR       Author name
  --email EMAIL         Author email
  --template-url TEMPLATE_URL
                        Ad-hoc template Git URL (bypasses template selection)
  --output-dir OUTPUT_DIR
                        Output directory (default: current directory)
  --no-cache            Skip cache and fetch fresh template
```

### File Locations

```
skills/init-project-cookiecutter/
├── SKILL.md                    # AI agent documentation
├── README.md                   # Quick start guide
├── USER_MANUAL.md              # This file
└── scripts/
    ├── init_project.py         # Main script
    └── template_sources.yaml   # Template registry

~/.claude/
├── cookiecutter_cache/         # Template cache
│   ├── bdd-cli-click/
│   ├── bdd-cli-typer/
│   └── bdd-cli-argparse/
└── template_sources_override.yaml  # User overrides
```

### Template Variables

Standard variables in cookiecutter templates:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `project_name` | string | Human-readable name | "My Project" |
| `project_slug` | string | Python package name | "my_project" |
| `project_short_description` | string | One-line description | "A CLI tool" |
| `cli_framework` | choice | CLI framework | "click" |
| `has_api_integration` | yes/no | Include API code | "yes" |
| `has_database_integration` | yes/no | Include database code | "no" |
| `has_files_integration` | yes/no | Include file processing | "yes" |
| `has_data_integration` | yes/no | Include data analysis | "no" |
| `author_name` | string | Author name | "John Doe" |
| `author_email` | string | Author email | "john@example.com" |
| `python_version` | string | Python version | "3.11" |
| `license` | choice | License type | "MIT" |

### Error Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error (validation, prerequisites, etc.) |
| 130 | Interrupted by user (Ctrl+C) |

### Git URL Formats

Supported formats:

```
# GitHub shorthand
gh:username/repo
gh:username/repo --checkout branch-name
gh:username/repo --directory subdirectory

# GitLab shorthand
gl:username/repo

# Bitbucket shorthand
bb:username/repo

# Full HTTPS
https://github.com/username/repo.git
https://gitlab.com/username/repo.git

# SSH
git@github.com:username/repo.git
git@gitlab.com:username/repo.git

# With credentials (HTTPS)
https://TOKEN@github.com/username/repo.git
```

### Integration Comparison

| Integration | Dependencies | Use Case | Adds Files |
|-------------|-------------|----------|------------|
| `api` | httpx, responses | HTTP API client | api_client.py |
| `database` | sqlalchemy, psycopg2 | Database operations | database.py, models.py |
| `files` | pypdf2, python-magic | File processing | file_handler.py |
| `data` | pandas, numpy | Data analysis | data_processor.py |

### Resources

- **Cookiecutter**: https://cookiecutter.readthedocs.io/
- **Behave (BDD)**: https://behave.readthedocs.io/
- **Gherkin Syntax**: https://cucumber.io/docs/gherkin/
- **uv Package Manager**: https://docs.astral.sh/uv/
- **Click Framework**: https://click.palletsprojects.com/
- **Typer Framework**: https://typer.tiangolo.com/
- **Python Argparse**: https://docs.python.org/3/library/argparse.html

---

## Appendix

### Glossary

**BDD (Behavior-Driven Development)**: Development methodology that uses human-readable descriptions of software behavior (Gherkin) to drive development and testing.

**Gherkin**: Language for writing BDD scenarios using Given-When-Then format.

**Behave**: Python BDD framework that runs Gherkin scenarios.

**Cookiecutter**: Tool for generating projects from templates.

**Template**: Parameterized project structure with variables that get replaced during generation.

**Integration**: Optional functionality (API, database, files, data) included in generated project.

**Hook**: Script that runs before (`pre_gen_project.py`) or after (`post_gen_project.py`) template generation.

**Registry**: Configuration file (`template_sources.yaml`) mapping requirements to Git template URLs.

**Priority**: Numeric value determining template selection order (lower = higher priority).

### Version History

- **v2.0.0** (2026-01): Git-based template architecture
- **v1.0.0** (2025): Initial script-based generation

### License

This skill and documentation are released under the MIT License.

---

**End of User Manual**

For additional help:
- Check SKILL.md for AI agent integration
- See README.md for quick start
- Review BDD_IMPLEMENTATION_GUIDE.md for BDD workflow
- Report issues to project repository
