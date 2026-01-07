---
name: init-project-cookiecutter
description: Initialize a new BDD-based CLI project using cookiecutter templates from Git repositories. This skill intelligently selects and fetches the appropriate template based on user requirements, supporting templates distributed across multiple Git projects.
compatibility: Requires cookiecutter, git, and uv package manager. Python 3.11+ recommended. Works on macOS, Linux, and Windows.
license: MIT
metadata:
  automation_level: full
  skill_category: project-initialization
  version: 2.0.0
  replaces: init-bdd-project (v1.0.0)
  architecture: git-based-templates
---

# init-project-cookiecutter Skill

## Purpose

This skill automates BDD-based CLI project initialization using **cookiecutter** templates stored in **Git repositories**. This distributed architecture allows:

- **Templates in Git**: Templates live in version-controlled repositories
- **Distributed Across Projects**: Templates can be in different repos/organizations
- **Dynamic Discovery**: No need for local template copies
- **Easy Extension**: Add new templates by referencing Git URLs
- **Version Control**: Use branches/tags for template versions
- **Team Collaboration**: Share templates across teams via Git

## Architecture Overview

```
User Requirements
       ↓
Template Selection (template_sources.yaml)
       ↓
Git URL Resolution (gh:org/repo, https://...)
       ↓
Cookiecutter Fetch (clone from Git)
       ↓
Project Generation
       ↓
Post-Setup (git init, uv sync, tests)
```

### Key Components

1. **template_sources.yaml**: Maps requirements to Git repository URLs
2. **Template Repositories**: Git repos containing cookiecutter templates
3. **Selection Logic**: Intelligently picks the right template
4. **Cache System**: Avoids re-cloning templates (configurable)
5. **Orchestration Script**: Coordinates the entire process

## How Templates are Stored

### Git Repository Patterns

Templates can be organized in several ways:

#### Pattern 1: Dedicated Template Repository
```
github.com/your-org/bdd-cli-click-template/
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

**Usage in template_sources.yaml**:
```yaml
templates:
  bdd-cli-click:
    git_url: "gh:your-org/bdd-cli-click-template"
```

#### Pattern 2: Monorepo with Multiple Templates
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

**Usage in template_sources.yaml**:
```yaml
templates:
  bdd-cli-click:
    git_url: "gh:your-org/python-templates"
    directory: "cli-templates/bdd-click"

  bdd-cli-typer:
    git_url: "gh:your-org/python-templates"
    directory: "cli-templates/bdd-typer"
```

#### Pattern 3: Versioned Templates with Branches/Tags
```
github.com/your-org/bdd-cli-template/
├── (main branch - latest stable)
├── (develop branch - bleeding edge)
└── (tags: v1.0.0, v2.0.0, v2.1.0)
```

**Usage in template_sources.yaml**:
```yaml
templates:
  bdd-cli-click-stable:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "v2.0.0"

  bdd-cli-click-latest:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "main"

  bdd-cli-click-dev:
    git_url: "gh:your-org/bdd-cli-template"
    checkout: "develop"
```

## Configuring Template Sources

### Main Configuration File

**Location**: `scripts/template_sources.yaml`

This file maps project requirements to Git repository URLs:

```yaml
version: "2.0.0"

templates:
  bdd-cli-click:
    name: "BDD CLI with Click Framework"
    description: "Full-featured BDD-based CLI using Click"
    git_url: "gh:your-org/bdd-cli-click-template"  # GitHub shorthand
    # directory: "optional/subdirectory"            # If in subdirectory
    # checkout: "v2.0.0"                             # Branch, tag, or commit
    framework: "click"
    supports_integrations:
      - api
      - database
      - files
      - data
    priority: 1
    status: "stable"

  bdd-cli-typer:
    name: "BDD CLI with Typer Framework"
    git_url: "gl:your-group/bdd-cli-typer-template"  # GitLab shorthand
    framework: "typer"
    supports_integrations:
      - api
      - database
      - files
      - data
    priority: 2
    status: "stable"

  bdd-cli-argparse:
    name: "BDD CLI with Argparse"
    git_url: "https://git.example.com/templates/bdd-argparse.git"  # Full URL
    framework: "argparse"
    supports_integrations:
      - api
      - files
    priority: 3
    status: "stable"
```

### Git URL Formats

Cookiecutter supports multiple Git URL formats:

```yaml
# GitHub shorthand
git_url: "gh:username/repo-name"

# GitLab shorthand
git_url: "gl:username/repo-name"

# Bitbucket shorthand
git_url: "bb:username/repo-name"

# Full HTTPS URL
git_url: "https://github.com/username/repo-name.git"

# SSH URL
git_url: "git@github.com:username/repo-name.git"

# With subdirectory
git_url: "gh:username/monorepo"
directory: "templates/specific-template"

# With version
git_url: "gh:username/repo-name"
checkout: "v2.0.0"  # Can be branch, tag, or commit SHA
```

### User Override File

Users can add custom templates without modifying the main configuration:

**Location**: `~/.claude/template_sources_override.yaml`

```yaml
version: "2.0.0"

templates:
  my-custom-template:
    name: "My Custom BDD Template"
    git_url: "gh:myusername/my-custom-template"
    framework: "click"
    supports_integrations:
      - api
    priority: 10
    status: "experimental"
```

The skill will merge both files, with user overrides taking precedence.

## User Requirements Collection

When invoked, the skill collects:

### 1. Project Name
```
What should your project be called?
Examples: "data-validator", "api-client", "log-analyzer"

Requirements:
- Must start with a letter
- Can contain: letters, numbers, hyphens, underscores
- Will be converted to snake_case for Python package name
```

### 2. CLI Framework
```
Which CLI framework do you prefer?

1. click    - Full-featured, decorator-based (most popular)
               Best for: Complex CLIs with many subcommands

2. typer    - Modern, type-hint based (Click-powered)
               Best for: Type-safe CLIs, FastAPI-style interface

3. argparse - Standard library, minimal dependencies
               Best for: Simple CLIs, maximum portability
```

### 3. Project Domain (Optional)
```
What does your tool do?
Examples:
- "Validates CSV data files against schemas"
- "Manages cloud deployment configurations"
- "Analyzes log files for patterns"

This helps customize documentation and example code.
```

### 4. Integrations (Optional)
```
What will your tool integrate with? (comma-separated or press Enter to skip)

- api      : Making HTTP requests to external APIs
- database : Storing or querying data with SQLAlchemy
- files    : Processing files (PDFs, images, documents)
- data     : Data analysis with pandas/numpy

Examples:
- "api"
- "api,database"
- "files,data"
```

## Template Selection Process

### Selection Algorithm

```python
def select_template(framework, integrations):
    """
    Select appropriate template based on requirements.

    Algorithm:
    1. Load template_sources.yaml
    2. Filter templates by framework (if specified)
    3. Check integration support
    4. Apply priority ordering
    5. Validate template availability
    6. Return selected template or error
    """

    # Load sources
    templates = load_template_sources()

    # Filter by framework
    if framework:
        candidates = [t for t in templates if t.framework == framework]
    else:
        candidates = templates

    # Check integration support
    if integrations:
        candidates = [t for t in candidates
                      if all(i in t.supports_integrations for i in integrations)]

    # Sort by priority
    candidates.sort(key=lambda t: t.priority)

    # Return best match or error
    if candidates:
        return candidates[0]
    else:
        raise TemplateNotFoundError(
            f"No template found for framework={framework}, integrations={integrations}"
        )
```

### Selection Examples

```python
# Example 1: User specifies Click framework
requirements = {"framework": "click", "integrations": []}
# → Selects: bdd-cli-click

# Example 2: User wants Typer with API integration
requirements = {"framework": "typer", "integrations": ["api"]}
# → Selects: bdd-cli-typer (must support 'api' integration)

# Example 3: No framework specified, needs database + files
requirements = {"framework": None, "integrations": ["database", "files"]}
# → Selects: Highest priority template supporting both integrations

# Example 4: Argparse with unsupported integration
requirements = {"framework": "argparse", "integrations": ["data"]}
# → Error if bdd-cli-argparse doesn't support 'data' integration
```

## For AI Agents: Invocation Guide

### Prerequisites

```bash
# Required tools
- cookiecutter: pip install cookiecutter (or uv tool install cookiecutter)
- git: Standard git installation
- uv: curl -LsSf https://astral.sh/uv/install.sh | sh
- Python 3.11+
```

### Locating the Skill

```bash
# Check common skill locations
SKILL_LOCATIONS=(
    "${HOME}/.claude/skills/init-project-cookiecutter"
    "$(pwd)/.claude/skills/init-project-cookiecutter"
    "$(pwd)/skills/init-project-cookiecutter"
)

for location in "${SKILL_LOCATIONS[@]}"; do
    if [ -f "${location}/scripts/init_project.py" ]; then
        SKILL_PATH="${location}"
        break
    fi
done
```

### Invocation Modes

#### Interactive Mode (Recommended for Agents)
```bash
uv run python "${SKILL_PATH}/scripts/init_project.py" --interactive
```

The script will:
1. Display available templates (from Git)
2. Ask user questions
3. Select appropriate template
4. Fetch from Git repository
5. Generate project
6. Run post-setup

#### Non-Interactive Mode
```bash
uv run python "${SKILL_PATH}/scripts/init_project.py" \
    --name "data-validator" \
    --framework "click" \
    --domain "CSV data validation tool" \
    --integrations "files,api" \
    --author "Jane Doe" \
    --email "jane@example.com"
```

#### List Available Templates
```bash
uv run python "${SKILL_PATH}/scripts/init_project.py" --list-templates
```

Output:
```
Available Templates (from Git repositories):

bdd-cli-click (priority: 1) [stable]
  Repository: gh:your-org/bdd-cli-click-template
  Framework: click
  Integrations: api, database, files, data
  Description: Full-featured BDD-based CLI using Click

bdd-cli-typer (priority: 2) [stable]
  Repository: gl:your-group/bdd-cli-typer-template
  Framework: typer
  Integrations: api, database, files, data
  Description: Modern BDD-based CLI using Typer

bdd-cli-argparse (priority: 3) [stable]
  Repository: https://git.example.com/templates/bdd-argparse.git
  Framework: argparse
  Integrations: api, files
  Description: BDD-based CLI using argparse
```

#### Ad-hoc Template URL
```bash
# Use a template not in template_sources.yaml
uv run python "${SKILL_PATH}/scripts/init_project.py" \
    --name "my-project" \
    --template-url "gh:someone-else/their-template"
```

#### Preview Template (without generating)
```bash
uv run python "${SKILL_PATH}/scripts/init_project.py" \
    --preview-template "bdd-cli-click"
```

Shows:
- Template Git URL
- Cookiecutter variables
- Estimated project structure
- Required integrations

### Complete Agent Workflow

```python
import subprocess
from pathlib import Path

def initialize_bdd_project():
    """Complete workflow for AI agent."""

    # 1. Locate skill
    skill_path = Path.home() / ".claude/skills/init-project-cookiecutter"
    script = skill_path / "scripts/init_project.py"

    if not script.exists():
        raise FileNotFoundError("Skill not found")

    # 2. Gather requirements (interactive or programmatic)
    requirements = {
        "name": "data-validator",
        "framework": "click",
        "domain": "CSV data validation tool",
        "integrations": "files,api",
        "author": "Your Name",
        "email": "you@example.com"
    }

    # 3. Build command
    cmd = [
        "uv", "run", "python", str(script),
        "--name", requirements["name"],
        "--framework", requirements["framework"],
        "--domain", requirements["domain"],
        "--integrations", requirements["integrations"],
        "--author", requirements["author"],
        "--email", requirements["email"]
    ]

    # 4. Execute
    print("Fetching template from Git and generating project...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 5. Handle result
    if result.returncode == 0:
        print("✓ Project initialized successfully!")
        print(result.stdout)

        # 6. Next steps
        project_dir = Path.cwd() / requirements["name"].replace("-", "_")
        print(f"\nNext steps:")
        print(f"  cd {project_dir}")
        print(f"  source .venv/bin/activate")
        print(f"  uv run behave")
    else:
        print("✗ Failed:")
        print(result.stderr)
        raise RuntimeError("Project initialization failed")
```

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `TemplateNotFoundError` | No template matches requirements | Check available templates with `--list-templates` |
| `GitCloneError` | Failed to clone template repo | Verify Git URL, check network, ensure repo accessibility |
| `InvalidGitURLError` | Malformed Git URL | Check format: `gh:user/repo`, `https://...`, etc. |
| `TemplateValidationError` | Invalid cookiecutter.json | Fix template in Git repository |
| `IntegrationNotSupportedError` | Template doesn't support requested integration | Choose different template or remove integration |
| `PrerequisiteError` | Missing cookiecutter/git/uv | Install missing tools |

## Template Caching

### How Caching Works

To avoid repeatedly cloning the same template:

1. **First fetch**: Template cloned to `~/.claude/cookiecutter_cache/<template-id>/`
2. **Subsequent fetches**: Cached copy used if fresh (< 7 days by default)
3. **Cache refresh**: Automatically pulls latest changes if cache expired
4. **Manual refresh**: Use `--no-cache` flag to force fresh clone

### Cache Configuration

In `template_sources.yaml`:

```yaml
cache:
  enabled: true
  location: "~/.claude/cookiecutter_cache"
  ttl_days: 7  # Re-clone templates older than this
  auto_clean: true  # Clean expired entries
```

### Cache Management

```bash
# List cached templates
python scripts/init_project.py --list-cache

# Clear cache
python scripts/init_project.py --clear-cache

# Clear specific template
python scripts/init_project.py --clear-cache --template "bdd-cli-click"

# Disable cache for single run
python scripts/init_project.py --no-cache --name "my-project" ...
```

## Creating Your Own Templates

### Step 1: Create Cookiecutter Template

```bash
mkdir my-bdd-template
cd my-bdd-template
```

### Step 2: Create cookiecutter.json

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

### Step 3: Create Template Structure

```bash
mkdir -p "{{cookiecutter.project_slug}}/src/{{cookiecutter.project_slug}}"
# Add all template files with {{cookiecutter.variable}} placeholders
```

### Step 4: Add Hooks (Optional)

```bash
mkdir hooks
```

**hooks/pre_gen_project.py**:
```python
"""Validate before generation."""
import re
import sys

slug = "{{ cookiecutter.project_slug }}"
if not re.match(r'^[a-z][a-z0-9_]*$', slug):
    print(f"Error: Invalid project_slug '{slug}'")
    sys.exit(1)
```

**hooks/post_gen_project.py**:
```python
"""Setup after generation."""
import subprocess
from pathlib import Path

# Initialize git
subprocess.run(["git", "init"])
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "Initial commit"])

# Setup Python environment
subprocess.run(["uv", "venv"])
subprocess.run(["uv", "sync"])

print("\n✓ Project ready!")
```

### Step 5: Push to Git

```bash
git init
git add .
git commit -m "Initial template"
git remote add origin git@github.com:your-org/my-bdd-template.git
git push -u origin main
```

### Step 6: Register Template

Add to `template_sources.yaml`:

```yaml
templates:
  my-custom-bdd:
    name: "My Custom BDD Template"
    description: "Custom BDD template with special features"
    git_url: "gh:your-org/my-bdd-template"
    framework: "click"
    supports_integrations:
      - api
      - files
    priority: 10
    status: "experimental"
```

### Step 7: Test Template

```bash
python scripts/init_project.py \
    --name "test-project" \
    --framework "click" \
    --template-url "gh:your-org/my-bdd-template"
```

## Best Practices

### For Template Authors

1. **Version Your Templates**: Use Git tags (v1.0.0, v2.0.0)
2. **Document Variables**: Comment cookiecutter.json thoroughly
3. **Test Generated Projects**: Ensure they work out-of-the-box
4. **Use Hooks Wisely**: Keep pre/post generation logic simple
5. **Follow Conventions**: Match structure of existing templates
6. **Provide Examples**: Include example code in generated projects

### For Template Users

1. **Pin Template Versions**: Use `checkout: "v1.0.0"` for stability
2. **Review Generated Code**: Templates are starting points
3. **Customize After Generation**: Adapt to your needs
4. **Report Issues**: Help improve templates
5. **Share Templates**: Contribute back useful templates

### For Template Managers

1. **Organize Templates**: Group by framework, use case, or team
2. **Maintain Documentation**: Keep template_sources.yaml documented
3. **Regular Updates**: Keep templates current with best practices
4. **Quality Control**: Review templates before adding to registry
5. **Version Management**: Deprecate old versions gracefully

## Troubleshooting

### Git Clone Failures

```bash
# Test Git URL directly
git clone gh:your-org/template-name /tmp/test-clone

# Check SSH keys
ssh -T git@github.com

# Use HTTPS instead
git_url: "https://github.com/your-org/template-name.git"
```

### Template Not Found

```bash
# List all registered templates
python scripts/init_project.py --list-templates

# Check template_sources.yaml syntax
python -c "import yaml; yaml.safe_load(open('scripts/template_sources.yaml'))"
```

### Integration Not Supported

```bash
# Check what integrations a template supports
python scripts/init_project.py --preview-template "bdd-cli-click"

# Use a different template or remove the integration from requirements
```

## Comparison with Other Approaches

| Feature | Script Generation | Local Templates | Git-Based Templates |
|---------|------------------|-----------------|---------------------|
| Storage | In Python code | Local filesystem | Git repositories |
| Versioning | Code versions | Manual copies | Git tags/branches |
| Sharing | Share script | Share files | Share Git URL |
| Updates | Modify code | Replace files | Git pull |
| Extensibility | Edit script | Add directories | Add Git repos |
| Distribution | Monolithic | Per-project | Distributed |
| Team collaboration | Limited | Manual sync | Native (Git) |
| This approach | v1.0 | Traditional | **v2.0 (current)** |

## Reference

- **Cookiecutter Docs**: https://cookiecutter.readthedocs.io/
- **Git URL Formats**: https://cookiecutter.readthedocs.io/en/stable/usage.html#works-directly-with-git-and-hg-mercurial-repos-too
- **BDD Implementation Guide**: ../BDD_IMPLEMENTATION_GUIDE.md
- **Template Repository Examples**: See template_sources.yaml for URLs

## License

MIT License - Free to use and modify
