# init-project-cookiecutter Skill

Initialize BDD-based CLI projects using cookiecutter templates from Git repositories.

## Quick Start

```bash
# Interactive mode (recommended)
python scripts/init_project.py --interactive

# Non-interactive mode
python scripts/init_project.py \
    --name "my-project" \
    --framework "click" \
    --integrations "api,files"

# List available templates
python scripts/init_project.py --list-templates
```

## Architecture

This skill uses a **Git-based template architecture**:

- Templates are stored in Git repositories (not local files)
- `template_sources.yaml` maps requirements to Git URLs
- Cookiecutter fetches templates on-demand
- Supports GitHub, GitLab, Bitbucket, and custom Git servers
- Optional caching to avoid re-cloning

## Key Files

- **SKILL.md**: Complete documentation for AI agents and users
- **scripts/init_project.py**: Main orchestration script
- **scripts/template_sources.yaml**: Template registry (Git URLs)

## Prerequisites

```bash
# Required
pip install cookiecutter pyyaml
# Or: uv tool install cookiecutter && pip install pyyaml

# Verify
cookiecutter --version
git --version
python --version  # 3.11+ required
```

## Configuration

### Adding Custom Templates

Edit `scripts/template_sources.yaml`:

```yaml
templates:
  my-custom-template:
    name: "My Custom BDD Template"
    git_url: "gh:your-org/your-template"
    framework: "click"
    supports_integrations:
      - api
      - files
    priority: 10
    status: "experimental"
```

### User Overrides

Create `~/.claude/template_sources_override.yaml` for personal templates:

```yaml
version: "2.0.0"
templates:
  personal-template:
    git_url: "gh:myusername/my-template"
    framework: "typer"
```

## Usage Examples

### Example 1: Data Validation Tool

```bash
python scripts/init_project.py \
    --name "data-validator" \
    --framework "click" \
    --domain "CSV data validation tool" \
    --integrations "files" \
    --author "Jane Doe" \
    --email "jane@example.com"
```

### Example 2: API Client with Database

```bash
python scripts/init_project.py \
    --name "api-client" \
    --framework "typer" \
    --domain "REST API client with caching" \
    --integrations "api,database"
```

### Example 3: Ad-hoc Template URL

```bash
python scripts/init_project.py \
    --name "my-project" \
    --template-url "gh:someone-else/their-template"
```

## Template Repository Patterns

### Pattern 1: Dedicated Repository
```
github.com/org/bdd-cli-click-template/
├── cookiecutter.json
├── hooks/
└── {{cookiecutter.project_slug}}/
```

Usage:
```yaml
git_url: "gh:org/bdd-cli-click-template"
```

### Pattern 2: Monorepo with Subdirectories
```
github.com/org/python-templates/
├── cli-templates/
│   ├── bdd-click/
│   └── bdd-typer/
```

Usage:
```yaml
git_url: "gh:org/python-templates"
directory: "cli-templates/bdd-click"
```

### Pattern 3: Versioned with Tags
```
github.com/org/bdd-template/
├── (main branch)
└── (tags: v1.0.0, v2.0.0)
```

Usage:
```yaml
git_url: "gh:org/bdd-template"
checkout: "v2.0.0"
```

## Creating Your Own Templates

1. **Create cookiecutter structure**:
   ```bash
   mkdir my-template
   cd my-template
   # Create cookiecutter.json and {{cookiecutter.project_slug}}/
   ```

2. **Push to Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial template"
   git remote add origin git@github.com:org/my-template.git
   git push -u origin main
   ```

3. **Register in template_sources.yaml**:
   ```yaml
   templates:
     my-template:
       git_url: "gh:org/my-template"
       framework: "click"
   ```

4. **Test**:
   ```bash
   python scripts/init_project.py --name "test" --template-url "gh:org/my-template"
   ```

## Troubleshooting

### "cookiecutter: command not found"
```bash
pip install cookiecutter
# Or: uv tool install cookiecutter
# Or: pipx install cookiecutter
```

### Git Clone Failures
```bash
# Test Git URL directly
git clone gh:org/template /tmp/test

# Check SSH keys
ssh -T git@github.com

# Use HTTPS instead of SSH
git_url: "https://github.com/org/template.git"
```

### Template Not Found
```bash
# List available templates
python scripts/init_project.py --list-templates

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('scripts/template_sources.yaml'))"
```

## For AI Agents

See **SKILL.md** for complete AI agent invocation guide, including:
- Prerequisite checking
- Skill location discovery
- Error handling
- Complete workflow examples

## Documentation

- **SKILL.md**: Complete skill documentation
- **BDD_IMPLEMENTATION_GUIDE.md**: BDD workflow guide (in parent directory)
- **Cookiecutter Docs**: https://cookiecutter.readthedocs.io/

## License

MIT
