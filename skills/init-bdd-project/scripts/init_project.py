#!/usr/bin/env python3
"""
BDD Project Initialization Script

Creates a complete BDD-based CLI project with:
- Directory structure (src/, tests/, features/)
- Configured pyproject.toml
- Behave setup (environment.py, behave.ini)
- Template feature files
- .gitignore and README.md
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def check_prerequisites() -> None:
    """
    Check that all required tools are installed.

    Raises:
        RuntimeError: If any required tool is missing or version is incompatible
    """
    errors = []

    # Check for uv
    if not shutil.which("uv"):
        errors.append(
            "uv is not installed.\n"
            "  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "  Or visit: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # Check Python version
    version_info = sys.version_info
    if version_info < (3, 11):
        errors.append(
            f"Python 3.11+ is required, but you have {version_info.major}.{version_info.minor}.\n"
            "  Install Python 3.11+ from https://www.python.org/downloads/"
        )

    # Check for git (optional but recommended)
    if not shutil.which("git"):
        print("Warning: git is not installed. You won't be able to initialize a git repository.")
        print("  Install git from: https://git-scm.com/downloads")
        print()

    if errors:
        error_message = "Missing prerequisites:\n\n" + "\n\n".join(f"• {error}" for error in errors)
        raise RuntimeError(error_message)


def validate_project_name(name: str) -> str:
    """
    Validate and normalize project name.

    Args:
        name: Raw project name input

    Returns:
        Normalized project name (snake_case)

    Raises:
        ValueError: If name is invalid
    """
    # Convert to snake_case
    normalized = name.lower().replace("-", "_").replace(" ", "_")

    # Validate
    if not normalized:
        raise ValueError("Project name cannot be empty")

    if not normalized[0].isalpha():
        raise ValueError("Project name must start with a letter")

    if not all(c.isalnum() or c == "_" for c in normalized):
        raise ValueError("Project name can only contain letters, numbers, and underscores")

    # Check it's not a Python keyword
    import keyword
    if keyword.iskeyword(normalized):
        raise ValueError(f"Project name '{normalized}' is a Python keyword")

    return normalized


def create_directory_structure(base_path: Path, project_name: str) -> dict[str, Path]:
    """
    Create the complete directory structure.

    Args:
        base_path: Base directory for the project
        project_name: Normalized project name

    Returns:
        Dictionary mapping directory names to Path objects
    """
    # Project root
    project_root = base_path / project_name

    if project_root.exists():
        raise FileExistsError(f"Directory '{project_root}' already exists")

    # Define structure
    dirs = {
        "root": project_root,
        "src": project_root / "src" / project_name,
        "core": project_root / "src" / project_name / "core",
        "infrastructure": project_root / "src" / project_name / "infrastructure",
        "services": project_root / "src" / project_name / "services",
        "cli": project_root / "src" / project_name / "cli",
        "config": project_root / "src" / project_name / "config",
        "tests": project_root / "tests",
        "tests_unit": project_root / "tests" / "unit",
        "tests_integration": project_root / "tests" / "integration",
        "features": project_root / "features",
        "steps": project_root / "features" / "steps",
    }

    # Create all directories
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return dirs


def get_dependencies(framework: str, integrations: list[str]) -> dict[str, list[str]]:
    """
    Determine dependencies based on framework and integrations.

    Args:
        framework: CLI framework (click, typer, argparse)
        integrations: List of integration types

    Returns:
        Dictionary with 'core' and 'dev' dependency lists
    """
    core_deps = [
        "pydantic>=2.0",
        "structlog>=24.0",
        "rich>=13.0",
        "pyyaml>=6.0",
    ]

    # Add CLI framework
    if framework == "click":
        core_deps.append("click>=8.1")
    elif framework == "typer":
        core_deps.append("typer>=0.12")
    # argparse is stdlib

    # Add integration-specific dependencies
    if "api" in integrations:
        core_deps.extend(["httpx>=0.27"])

    if "database" in integrations:
        core_deps.extend(["sqlalchemy>=2.0", "psycopg2-binary>=2.9"])

    if "files" in integrations:
        core_deps.extend(["pypdf2>=3.0", "python-magic-bin>=0.4"])

    if "data" in integrations:
        core_deps.extend(["pandas>=2.0", "numpy>=1.24"])

    # Development dependencies
    dev_deps = [
        "pytest>=8.0",
        "pytest-cov>=4.1",
        "pytest-mock>=3.12",
        "mypy>=1.8",
        "ruff>=0.6",
        "behave>=1.2.6",
        "freezegun>=1.4",
    ]

    # Add test dependencies for integrations
    if "api" in integrations:
        dev_deps.append("responses>=0.25")

    return {"core": core_deps, "dev": dev_deps}


def generate_pyproject_toml(
    project_name: str,
    framework: str,
    integrations: list[str],
    domain: str | None = None,
) -> str:
    """
    Generate pyproject.toml content.

    Args:
        project_name: Project name
        framework: CLI framework
        integrations: List of integration types
        domain: Project domain/description

    Returns:
        Content for pyproject.toml
    """
    deps = get_dependencies(framework, integrations)

    # Build description
    desc = domain if domain else f"A CLI application built with BDD"

    # Format dependencies
    core_deps_str = "\n    ".join(f'"{dep}",' for dep in deps["core"])
    dev_deps_str = "\n    ".join(f'"{dep}",' for dep in deps["dev"])

    # Entry point based on framework
    entry_point = f"{project_name}.cli.main:cli" if framework in ["click", "typer"] else f"{project_name}.cli.main:main"

    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "{desc}"
readme = "README.md"
requires-python = ">=3.11"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "you@example.com"}},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    {core_deps_str}
]

[project.optional-dependencies]
dev = [
    {dev_deps_str}
]

[project.scripts]
{project_name} = "{entry_point}"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "RUF", # ruff-specific rules
]
ignore = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/*" = ["S101"]      # Allow assert in tests

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
no_implicit_reexport = true
strict_equality = true

[[tool.mypy.overrides]]
module = "behave.*"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov={project_name}",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
'''

    return content


def generate_environment_py(integrations: list[str]) -> str:
    """
    Generate Behave environment.py with hooks for integrations.

    Args:
        integrations: List of integration types

    Returns:
        Content for environment.py
    """
    has_api = "api" in integrations
    has_db = "database" in integrations

    content = '''"""Behave environment setup and teardown."""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any


def before_all(context: Any) -> None:
    """Run before all tests."""
    # Store original environment
    context.original_env = os.environ.copy()

    # Set test environment variables
    os.environ["TEST_MODE"] = "true"
'''

    if has_api:
        content += '''    # API testing (customize for your API)
    os.environ["API_KEY"] = "test-api-key"
    os.environ["API_BASE_URL"] = "http://localhost:8000"
'''

    if has_db:
        content += '''    # Database testing
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
'''

    content += '''
    # Store original working directory
    context.original_cwd = Path.cwd()

    # Initialize test data storage
    context.test_data = {}


def before_feature(context: Any, feature: Any) -> None:
    """Run before each feature."""
    # Create temporary directory for this feature
    context.temp_dir = Path(tempfile.mkdtemp(prefix=f"test_{feature.name}_"))
    context.test_files = []
    context.output_files = []
'''

    if has_api:
        content += '''
    # Initialize mock API responses
    context.mock_responses = {}
'''

    if has_db:
        content += '''
    # Initialize test database
    from sqlalchemy import create_engine
    context.test_engine = create_engine(os.environ["DATABASE_URL"])
'''

    content += '''


def after_feature(context: Any, feature: Any) -> None:
    """Run after each feature."""
    # Clean up temporary directory
    if hasattr(context, "temp_dir") and context.temp_dir.exists():
        shutil.rmtree(context.temp_dir)

    # Change back to original directory
    os.chdir(context.original_cwd)
'''

    if has_db:
        content += '''
    # Clean up database
    if hasattr(context, "test_engine"):
        context.test_engine.dispose()
'''

    content += '''


def before_scenario(context: Any, scenario: Any) -> None:
    """Run before each scenario."""
    # Reset scenario-specific context
    context.current_file = None
    context.result = None
    context.error = None
    context.output = None
    context.config = None
    context.process = None
'''

    if has_api:
        content += '''    context.api_response = None
    context.status_code = None
'''

    content += '''
    # Create scenario-specific temp directory
    context.scenario_dir = context.temp_dir / scenario.name.replace(" ", "_")
    context.scenario_dir.mkdir(exist_ok=True)
    os.chdir(context.scenario_dir)


def after_scenario(context: Any, scenario: Any) -> None:
    """Run after each scenario."""
    # Clean up scenario-specific resources
    if hasattr(context, "client"):
        # Close any open connections
        if hasattr(context.client, "close"):
            context.client.close()
        delattr(context, "client")

    if hasattr(context, "process") and context.process:
        # Terminate any running processes
        if context.process.poll() is None:
            context.process.terminate()
            context.process.wait()


def after_all(context: Any) -> None:
    """Run after all tests."""
    # Restore original environment
    os.environ.clear()
    os.environ.update(context.original_env)

    # Change back to original directory
    os.chdir(context.original_cwd)
'''

    return content


def generate_behave_ini() -> str:
    """Generate behave.ini configuration."""
    return """[behave]
# Show scenario outlines as individual scenarios
show_skipped = false

# Don't capture stdout
stdout_capture = false

# Show full diff on assertion failures
show_failures = true

# Stop on first failure (useful during development)
# Uncomment during active development:
# stop = true

# Tag expression to run specific features
# Uncomment to run only specific tags:
# tags = @wip

# Format for output
format = pretty

# Logging level
logging_level = WARNING
"""


def generate_gitignore() -> str:
    """Generate .gitignore file."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.hypothesis/
*.cover
.cache

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ruff
.ruff_cache/

# Behave
behave_reports/

# Environment variables
.env
.env.local

# Project specific
*.log
*.db
*.sqlite
temp/
tmp/
"""


def generate_readme(project_name: str, framework: str, domain: str | None) -> str:
    """Generate README.md."""
    desc = domain if domain else "A CLI application"

    return f'''# {project_name}

{desc} built with BDD (Behavior-Driven Development) using Behave.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv sync
```

## Development

This project follows a BDD workflow using Gherkin specifications and Behave.

### Running Tests

```bash
# Run all BDD scenarios
uv run behave

# Run specific tags
uv run behave --tags=@wip       # Work in progress
uv run behave --tags=@passing   # All passing tests

# Run unit tests
uv run pytest

# Run with coverage
uv run pytest --cov
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

### BDD Workflow

1. Write feature in Gherkin (see `features/*.feature`)
2. Tag scenario as `@wip`
3. Run `behave --tags=@wip` (red)
4. Implement step definitions in `features/steps/`
5. Run tests again (still red)
6. Implement minimal code in `src/{project_name}/`
7. Run tests (green)
8. Refactor
9. Change tag to `@passing`

See `BDD_IMPLEMENTATION_GUIDE.md` for complete workflow details.

## Usage

```bash
# Install in development mode
uv pip install -e .

# Run the CLI
{project_name} --help
```

## Project Structure

```
{project_name}/
├── src/{project_name}/     # Source code
│   ├── core/              # Domain models
│   ├── infrastructure/    # External integrations
│   ├── services/          # Business logic
│   ├── cli/              # CLI interface
│   └── config/           # Configuration
├── tests/                # pytest tests
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── features/            # Behave BDD tests
│   ├── *.feature       # Gherkin scenarios
│   ├── steps/          # Step definitions
│   └── environment.py  # Test setup/teardown
├── pyproject.toml      # Project configuration
└── README.md          # This file
```

## License

MIT
'''


def generate_foundation_feature(project_name: str, framework: str) -> str:
    """Generate initial foundation feature file."""
    cli_example = f"{project_name} --help" if framework != "argparse" else f"python -m {project_name} --help"

    return f'''Feature: Foundation and Setup

  As a developer
  I want to verify the basic project structure
  So that I can build upon a solid foundation

  @passing
  Scenario: Project structure exists
    Given the project directory exists
    Then the following directories should exist:
      | directory                    |
      | src/{project_name}           |
      | src/{project_name}/core      |
      | src/{project_name}/infrastructure |
      | src/{project_name}/services  |
      | src/{project_name}/cli       |
      | src/{project_name}/config    |
      | tests/unit                   |
      | tests/integration            |
      | features/steps               |

  @passing
  Scenario: CLI is accessible
    When I run "{cli_example}"
    Then the command should succeed
    And the output should contain "Usage"

  @failing
  Scenario: Configuration loads successfully
    Given a configuration file "config.yaml" with content:
      """
      settings:
        debug: true
        log_level: INFO
      """
    When I load the configuration
    Then the configuration should be valid
    And the setting "debug" should be true
    And the setting "log_level" should be "INFO"
'''


def generate_common_steps() -> str:
    """Generate common step definitions."""
    return '''"""Common step definitions reusable across features."""
from behave import given, when, then
from pathlib import Path
import json
import os


# ============================================================================
# File Operations
# ============================================================================

@given('a file named "{filename}"')
def step_create_file(context, filename):
    """Create a file with default content."""
    file_path = context.scenario_dir / filename
    file_path.write_text("Sample content")
    context.current_file = file_path


@given('a file named "{filename}" with content')
def step_create_file_with_content(context, filename):
    """Create a file with specific content from docstring."""
    file_path = context.scenario_dir / filename
    file_path.write_text(context.text)
    context.current_file = file_path


@given('the project directory exists')
def step_project_exists(context):
    """Verify project directory exists."""
    # context.original_cwd is set in environment.py
    assert context.original_cwd.exists()
    context.project_root = context.original_cwd


# ============================================================================
# Directory Checks
# ============================================================================

@then('the following directories should exist')
def step_directories_exist(context):
    """Check that multiple directories exist."""
    for row in context.table:
        dir_path = context.project_root / row["directory"]
        assert dir_path.exists(), f"Directory does not exist: {dir_path}"
        assert dir_path.is_dir(), f"Path is not a directory: {dir_path}"


# ============================================================================
# Command Execution
# ============================================================================

@when('I run "{command}"')
def step_run_command(context, command):
    """Execute a CLI command."""
    import subprocess

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=context.scenario_dir,
            timeout=30,
        )
        context.result = result
        context.exit_code = result.returncode
        context.stdout = result.stdout
        context.stderr = result.stderr
        context.error = None
    except Exception as e:
        context.result = None
        context.error = e


# ============================================================================
# Assertions - Exit Codes
# ============================================================================

@then('the command should succeed')
def step_command_succeeds(context):
    """Assert command exited with code 0."""
    assert context.error is None, f"Command failed with error: {context.error}"
    assert context.exit_code == 0, \
        f"Expected exit code 0, got {context.exit_code}\\nStderr: {context.stderr}"


@then('the command should fail')
def step_command_fails(context):
    """Assert command exited with non-zero code."""
    assert context.exit_code != 0, "Expected command to fail but it succeeded"


# ============================================================================
# Assertions - Output
# ============================================================================

@then('the output should contain "{text}"')
def step_output_contains(context, text):
    """Assert stdout contains specific text."""
    assert text in context.stdout, \
        f"Expected '{text}' in output:\\n{context.stdout}"


@then('the output should not contain "{text}"')
def step_output_not_contains(context, text):
    """Assert stdout does not contain specific text."""
    assert text not in context.stdout, \
        f"Unexpected '{text}' found in output:\\n{context.stdout}"


# ============================================================================
# Assertions - Files
# ============================================================================

@then('a file named "{filename}" should exist')
def step_file_exists(context, filename):
    """Assert file exists."""
    file_path = context.scenario_dir / filename
    assert file_path.exists(), f"File does not exist: {filename}"
    context.output_file = file_path


@then('a file named "{filename}" should not exist')
def step_file_not_exists(context, filename):
    """Assert file does not exist."""
    file_path = context.scenario_dir / filename
    assert not file_path.exists(), f"File should not exist: {filename}"
'''


def generate_cli_main(project_name: str, framework: str) -> str:
    """Generate initial CLI main file."""
    if framework == "click":
        return f'''"""CLI entry point using Click."""
import click


@click.group()
@click.version_option()
def cli() -> None:
    """{project_name} - A BDD-built CLI application."""
    pass


@cli.command()
def hello() -> None:
    """Say hello."""
    click.echo("Hello from {project_name}!")


if __name__ == "__main__":
    cli()
'''
    elif framework == "typer":
        return f'''"""CLI entry point using Typer."""
import typer

app = typer.Typer()


@app.command()
def hello() -> None:
    """Say hello."""
    typer.echo("Hello from {project_name}!")


def cli() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    cli()
'''
    else:  # argparse
        return f'''"""CLI entry point using argparse."""
import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="{project_name}",
        description="A BDD-built CLI application",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Hello command
    hello_parser = subparsers.add_parser("hello", help="Say hello")

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "hello":
        print("Hello from {project_name}!")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def create_init_files(dirs: dict[str, Path]) -> None:
    """Create __init__.py files in all package directories."""
    init_paths = [
        dirs["src"],
        dirs["core"],
        dirs["infrastructure"],
        dirs["services"],
        dirs["cli"],
        dirs["config"],
        dirs["steps"],
    ]

    for path in init_paths:
        (path / "__init__.py").write_text('"""Package initialization."""\n')


def initialize_project(
    project_name: str,
    framework: str,
    domain: str | None = None,
    integrations: list[str] | None = None,
    base_path: Path | None = None,
) -> None:
    """
    Initialize a complete BDD project.

    Args:
        project_name: Name of the project
        framework: CLI framework (click, typer, argparse)
        domain: Optional domain description
        integrations: Optional list of integrations
        base_path: Base directory (defaults to current directory)
    """
    if integrations is None:
        integrations = []

    if base_path is None:
        base_path = Path.cwd()

    # Check prerequisites first
    check_prerequisites()

    # Validate and normalize project name
    normalized_name = validate_project_name(project_name)

    print(f"Initializing BDD project: {normalized_name}")
    print(f"  Framework: {framework}")
    print(f"  Domain: {domain or 'generic'}")
    print(f"  Integrations: {', '.join(integrations) if integrations else 'none'}")
    print()

    # Create directory structure
    print("Creating directory structure...")
    dirs = create_directory_structure(base_path, normalized_name)

    # Create __init__.py files
    print("Creating package files...")
    create_init_files(dirs)

    # Generate and write files
    print("Generating configuration files...")

    # pyproject.toml
    (dirs["root"] / "pyproject.toml").write_text(
        generate_pyproject_toml(normalized_name, framework, integrations, domain)
    )

    # .gitignore
    (dirs["root"] / ".gitignore").write_text(generate_gitignore())

    # README.md
    (dirs["root"] / "README.md").write_text(
        generate_readme(normalized_name, framework, domain)
    )

    # .python-version
    (dirs["root"] / ".python-version").write_text("3.11\n")

    # Behave files
    print("Setting up Behave...")
    (dirs["features"] / "environment.py").write_text(
        generate_environment_py(integrations)
    )
    (dirs["features"] / "behave.ini").write_text(generate_behave_ini())

    # Feature files
    print("Creating template features...")
    (dirs["features"] / "01_foundation.feature").write_text(
        generate_foundation_feature(normalized_name, framework)
    )

    # Step definitions
    (dirs["steps"] / "common_steps.py").write_text(generate_common_steps())

    # CLI main file
    print("Creating CLI entry point...")
    (dirs["cli"] / "main.py").write_text(
        generate_cli_main(normalized_name, framework)
    )

    print()
    print("✓ Project initialized successfully!")
    print()
    print("Next steps:")
    print(f"  1. cd {normalized_name}")
    print("  2. uv venv")
    print("  3. source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
    print("  4. uv sync")
    print("  5. uv run behave  # Run BDD tests")
    print("  6. Review features/01_foundation.feature")
    print()
    print("For the complete BDD workflow, see BDD_IMPLEMENTATION_GUIDE.md")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize a BDD-based CLI project"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project name (will be normalized to snake_case)",
    )
    parser.add_argument(
        "--framework",
        required=True,
        choices=["click", "typer", "argparse"],
        help="CLI framework to use",
    )
    parser.add_argument(
        "--domain",
        help="Project domain/description (optional)",
    )
    parser.add_argument(
        "--integrations",
        help="Comma-separated list of integrations (api,database,files,data)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Base path for project (default: current directory)",
    )

    args = parser.parse_args()

    # Parse integrations
    integrations = []
    if args.integrations:
        integrations = [i.strip() for i in args.integrations.split(",")]
        valid_integrations = {"api", "database", "files", "data"}
        invalid = set(integrations) - valid_integrations
        if invalid:
            print(f"Error: Invalid integrations: {', '.join(invalid)}")
            print(f"Valid options: {', '.join(valid_integrations)}")
            return 1

    try:
        initialize_project(
            project_name=args.name,
            framework=args.framework,
            domain=args.domain,
            integrations=integrations,
            base_path=args.path,
        )
        return 0
    except (ValueError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
