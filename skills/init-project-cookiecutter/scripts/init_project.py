#!/usr/bin/env python3
"""
BDD Project Initialization with Cookiecutter (Git-Based Templates)

This script initializes BDD-based CLI projects using cookiecutter templates
stored in Git repositories. Templates are dynamically fetched from configured
Git URLs, allowing distributed template management across multiple projects.

Architecture:
- Templates stored in Git repositories (not local files)
- Configuration in template_sources.yaml maps requirements → Git URLs
- Cookiecutter fetches templates on-demand
- Optional caching to avoid re-cloning
- Support for GitHub, GitLab, Bitbucket, and custom Git servers

Usage:
    # Interactive mode
    python init_project.py --interactive

    # Non-interactive mode
    python init_project.py --name "my-project" --framework "click"

    # List available templates
    python init_project.py --list-templates

    # Use ad-hoc template URL
    python init_project.py --name "my-project" --template-url "gh:org/repo"
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TemplateConfig:
    """Configuration for a cookiecutter template from Git."""
    template_id: str
    name: str
    description: str
    git_url: str
    directory: str | None = None
    checkout: str | None = None
    framework: str | None = None
    supports_integrations: list[str] | None = None
    priority: int = 99
    status: str = "stable"

    def get_cookiecutter_url(self) -> str:
        """Get the full cookiecutter URL with directory and checkout."""
        url = self.git_url

        # Add directory if specified
        if self.directory:
            url = f"{url} --directory={self.directory}"

        # Add checkout (branch/tag) if specified
        if self.checkout:
            url = f"{url} --checkout={self.checkout}"

        return url


@dataclass
class ProjectRequirements:
    """User requirements for project initialization."""
    name: str
    framework: str | None = None
    domain: str | None = None
    integrations: list[str] | None = None
    author: str = "Your Name"
    email: str = "you@example.com"


# ============================================================================
# Exceptions
# ============================================================================

class TemplateNotFoundError(Exception):
    """Raised when no template matches requirements."""
    pass


class GitCloneError(Exception):
    """Raised when Git clone fails."""
    pass


class InvalidGitURLError(Exception):
    """Raised when Git URL is malformed."""
    pass


class PrerequisiteError(Exception):
    """Raised when required tools are missing."""
    pass


class IntegrationNotSupportedError(Exception):
    """Raised when template doesn't support requested integration."""
    pass


# ============================================================================
# Prerequisites Check
# ============================================================================

def check_prerequisites() -> None:
    """
    Check that all required tools are installed.

    Raises:
        PrerequisiteError: If any required tool is missing
    """
    errors = []

    # Check for cookiecutter
    if not shutil.which("cookiecutter"):
        errors.append(
            "cookiecutter is not installed.\n"
            "  Install with: pip install cookiecutter\n"
            "  Or with uv: uv tool install cookiecutter\n"
            "  Or with pipx: pipx install cookiecutter"
        )

    # Check for git
    if not shutil.which("git"):
        errors.append(
            "git is not installed.\n"
            "  Install from: https://git-scm.com/downloads"
        )

    # Check for uv (recommended but not required)
    if not shutil.which("uv"):
        print("Warning: uv is not installed (recommended for Python dependency management)")
        print("  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print()

    # Check Python version
    version_info = sys.version_info
    if version_info < (3, 11):
        errors.append(
            f"Python 3.11+ is required, but you have {version_info.major}.{version_info.minor}.\n"
            "  Install Python 3.11+ from https://www.python.org/downloads/"
        )

    if errors:
        error_message = "Missing prerequisites:\n\n" + "\n\n".join(f"• {error}" for error in errors)
        raise PrerequisiteError(error_message)


# ============================================================================
# Template Configuration Loading
# ============================================================================

def load_template_sources(config_path: Path, user_override_path: Path | None = None) -> dict[str, TemplateConfig]:
    """
    Load template configurations from YAML file(s).

    Args:
        config_path: Path to main template_sources.yaml
        user_override_path: Optional path to user override file

    Returns:
        Dictionary mapping template IDs to TemplateConfig objects
    """
    # Load main configuration
    if not config_path.exists():
        raise FileNotFoundError(f"Template sources not found: {config_path}")

    with open(config_path) as f:
        main_config = yaml.safe_load(f)

    templates = {}

    # Parse main templates
    for template_id, template_data in main_config.get("templates", {}).items():
        templates[template_id] = TemplateConfig(
            template_id=template_id,
            name=template_data.get("name", template_id),
            description=template_data.get("description", ""),
            git_url=template_data["git_url"],
            directory=template_data.get("directory"),
            checkout=template_data.get("checkout"),
            framework=template_data.get("framework"),
            supports_integrations=template_data.get("supports_integrations", []),
            priority=template_data.get("priority", 99),
            status=template_data.get("status", "stable")
        )

    # Load and merge user overrides if present
    if user_override_path and user_override_path.exists():
        with open(user_override_path) as f:
            user_config = yaml.safe_load(f)

        for template_id, template_data in user_config.get("templates", {}).items():
            templates[template_id] = TemplateConfig(
                template_id=template_id,
                name=template_data.get("name", template_id),
                description=template_data.get("description", ""),
                git_url=template_data["git_url"],
                directory=template_data.get("directory"),
                checkout=template_data.get("checkout"),
                framework=template_data.get("framework"),
                supports_integrations=template_data.get("supports_integrations", []),
                priority=template_data.get("priority", 99),
                status=template_data.get("status", "experimental")
            )

    return templates


# ============================================================================
# Template Selection
# ============================================================================

def select_template(
    templates: dict[str, TemplateConfig],
    requirements: ProjectRequirements
) -> TemplateConfig:
    """
    Select the most appropriate template based on requirements.

    Algorithm:
    1. Filter by framework (if specified)
    2. Check integration support
    3. Sort by priority
    4. Return best match or error

    Args:
        templates: Available templates
        requirements: User requirements

    Returns:
        Selected template

    Raises:
        TemplateNotFoundError: If no suitable template found
        IntegrationNotSupportedError: If requested integration not supported
    """
    candidates = list(templates.values())

    # Filter by framework
    if requirements.framework:
        candidates = [t for t in candidates if t.framework == requirements.framework]

    # Filter by integration support
    if requirements.integrations:
        for integration in requirements.integrations:
            candidates = [
                t for t in candidates
                if integration in (t.supports_integrations or [])
            ]

        # Check if we filtered out everything
        if not candidates and requirements.integrations:
            raise IntegrationNotSupportedError(
                f"No template supports all requested integrations: {', '.join(requirements.integrations)}\n"
                f"Available integrations: api, database, files, data"
            )

    # Sort by priority (lower number = higher priority)
    candidates.sort(key=lambda t: t.priority)

    # Return best match
    if candidates:
        return candidates[0]
    else:
        raise TemplateNotFoundError(
            f"No template found for framework={requirements.framework}, "
            f"integrations={requirements.integrations}"
        )


# ============================================================================
# User Input Collection
# ============================================================================

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


def collect_requirements_interactive() -> ProjectRequirements:
    """
    Collect project requirements from user interactively.

    Returns:
        ProjectRequirements object
    """
    print("=" * 70)
    print("BDD CLI Project Initialization (Cookiecutter)")
    print("=" * 70)
    print()

    # Project name
    while True:
        name = input("Project name: ").strip()
        if not name:
            print("Error: Project name is required")
            continue
        try:
            normalized_name = validate_project_name(name)
            if normalized_name != name:
                print(f"  → Normalized to: {normalized_name}")
            break
        except ValueError as e:
            print(f"Error: {e}")
            continue

    # CLI Framework
    print("\nCLI Framework:")
    print("  1. click    - Full-featured, decorator-based (most popular)")
    print("  2. typer    - Modern, type-hint based (Click-powered)")
    print("  3. argparse - Standard library, minimal dependencies")
    print("  4. (skip)   - Let the system choose based on integrations")
    framework_choice = input("Choose (1-4): ").strip()
    framework_map = {"1": "click", "2": "typer", "3": "argparse", "4": None}
    framework = framework_map.get(framework_choice, None)

    # Domain
    print("\nWhat does your tool do? (optional)")
    domain = input("Domain: ").strip() or None

    # Integrations
    print("\nIntegrations (comma-separated, or press Enter to skip):")
    print("  - api      : HTTP/REST API clients")
    print("  - database : Database operations")
    print("  - files    : File processing (PDFs, images)")
    print("  - data     : Data analysis/transformation")
    integrations_input = input("Integrations: ").strip()
    integrations = [i.strip() for i in integrations_input.split(",") if i.strip()] if integrations_input else None

    # Author info
    print("\nAuthor information (optional):")
    author = input("Your name: ").strip() or "Your Name"
    email = input("Your email: ").strip() or "you@example.com"

    print()
    return ProjectRequirements(
        name=normalized_name,
        framework=framework,
        domain=domain,
        integrations=integrations,
        author=author,
        email=email
    )


# ============================================================================
# Template Invocation
# ============================================================================

def invoke_cookiecutter(
    template: TemplateConfig,
    requirements: ProjectRequirements,
    output_dir: Path,
    no_cache: bool = False
) -> Path:
    """
    Invoke cookiecutter with the selected template.

    Args:
        template: Selected template configuration
        requirements: User requirements
        output_dir: Directory where project will be created
        no_cache: If True, skip cache and fetch fresh

    Returns:
        Path to generated project

    Raises:
        GitCloneError: If template fetch fails
    """
    print(f"Fetching template from: {template.git_url}")
    if template.directory:
        print(f"  Subdirectory: {template.directory}")
    if template.checkout:
        print(f"  Version: {template.checkout}")
    print()

    # Build cookiecutter command
    cmd = ["cookiecutter", template.git_url, "--no-input"]

    # Add directory if specified
    if template.directory:
        cmd.extend(["--directory", template.directory])

    # Add checkout if specified
    if template.checkout:
        cmd.extend(["--checkout", template.checkout])

    # Add output directory
    cmd.extend(["--output-dir", str(output_dir)])

    # Add no-cache flag if requested
    if no_cache:
        cmd.append("--no-input")

    # Add template variables
    cmd.extend([
        f"project_name={requirements.name}",
        f"project_slug={requirements.name}",
        f"project_short_description={requirements.domain or 'A BDD-based CLI application'}",
        f"author_name={requirements.author}",
        f"author_email={requirements.email}",
    ])

    # Add integration flags
    if requirements.integrations:
        for integration in ["api", "database", "files", "data"]:
            value = "yes" if integration in requirements.integrations else "no"
            cmd.append(f"has_{integration}_integration={value}")

    # Execute cookiecutter
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            raise GitCloneError(
                f"Cookiecutter failed:\n{result.stderr}\n\n"
                f"Command: {' '.join(cmd)}"
            )

        # Determine project directory
        project_dir = output_dir / requirements.name

        if not project_dir.exists():
            raise FileNotFoundError(f"Project directory not created: {project_dir}")

        return project_dir

    except subprocess.TimeoutExpired:
        raise GitCloneError("Template fetch timed out (> 5 minutes)")
    except Exception as e:
        raise GitCloneError(f"Failed to fetch template: {e}")


# ============================================================================
# Post-Generation Setup
# ============================================================================

def run_post_setup(project_dir: Path) -> None:
    """
    Run post-generation setup tasks.

    Args:
        project_dir: Path to generated project
    """
    print("\nRunning post-generation setup...")

    original_dir = Path.cwd()
    try:
        import os
        os.chdir(project_dir)

        # Initialize git repository
        if shutil.which("git"):
            print("  • Initializing git repository...")
            subprocess.run(["git", "init"], capture_output=True, check=True)
            subprocess.run(["git", "add", "."], capture_output=True, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from cookiecutter template"],
                capture_output=True,
                check=True
            )

        # Set up Python environment with uv
        if shutil.which("uv"):
            print("  • Creating virtual environment...")
            subprocess.run(["uv", "venv"], capture_output=True, check=True)

            print("  • Installing dependencies...")
            subprocess.run(["uv", "sync"], capture_output=True, check=True)

            print("  • Running initial tests...")
            result = subprocess.run(
                ["uv", "run", "behave", "--dry-run"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ BDD tests structure verified")
            else:
                print("  ⚠ Warning: BDD tests verification failed")

        print("\n✓ Post-setup complete!")

    finally:
        import os
        os.chdir(original_dir)


# ============================================================================
# Display Functions
# ============================================================================

def list_templates(templates: dict[str, TemplateConfig]) -> None:
    """Display available templates."""
    print("\nAvailable Templates (from Git repositories):\n")

    sorted_templates = sorted(templates.values(), key=lambda t: t.priority)

    for template in sorted_templates:
        print(f"{template.template_id} (priority: {template.priority}) [{template.status}]")
        print(f"  Name: {template.name}")
        print(f"  Repository: {template.git_url}")
        if template.directory:
            print(f"  Directory: {template.directory}")
        if template.checkout:
            print(f"  Version: {template.checkout}")
        print(f"  Framework: {template.framework or 'any'}")
        if template.supports_integrations:
            print(f"  Integrations: {', '.join(template.supports_integrations)}")
        print(f"  Description: {template.description}")
        print()


# ============================================================================
# Main Function
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize BDD CLI project from Git-based cookiecutter template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s --interactive

  # Non-interactive mode
  %(prog)s --name "data-validator" --framework "click" --integrations "files,api"

  # List available templates
  %(prog)s --list-templates

  # Use custom template URL
  %(prog)s --name "my-project" --template-url "gh:org/custom-template"
        """
    )

    # Mode flags
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode (ask user for requirements)"
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit"
    )

    # Project configuration
    parser.add_argument("--name", help="Project name")
    parser.add_argument(
        "--framework",
        choices=["click", "typer", "argparse"],
        help="CLI framework"
    )
    parser.add_argument("--domain", help="Project domain/description")
    parser.add_argument(
        "--integrations",
        help="Comma-separated integrations (api,database,files,data)"
    )
    parser.add_argument("--author", default="Your Name", help="Author name")
    parser.add_argument("--email", default="you@example.com", help="Author email")

    # Template configuration
    parser.add_argument(
        "--template-url",
        help="Ad-hoc template Git URL (bypasses template selection)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )

    # Cache control
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cache and fetch fresh template"
    )

    args = parser.parse_args()

    try:
        # Check prerequisites
        check_prerequisites()

        # Determine script directory and config paths
        script_dir = Path(__file__).parent
        config_path = script_dir / "template_sources.yaml"
        user_override_path = Path.home() / ".claude" / "template_sources_override.yaml"

        # Load templates
        templates = load_template_sources(config_path, user_override_path)

        # Handle --list-templates
        if args.list_templates:
            list_templates(templates)
            return 0

        # Collect requirements
        if args.interactive:
            requirements = collect_requirements_interactive()
        elif args.name:
            # Parse integrations
            integrations = None
            if args.integrations:
                integrations = [i.strip() for i in args.integrations.split(",")]

            requirements = ProjectRequirements(
                name=validate_project_name(args.name),
                framework=args.framework,
                domain=args.domain,
                integrations=integrations,
                author=args.author,
                email=args.email
            )
        else:
            print("Error: Either --interactive or --name is required")
            print("Run with --help for usage information")
            return 1

        # Select or use custom template
        if args.template_url:
            # Create ad-hoc template config
            template = TemplateConfig(
                template_id="custom",
                name="Custom Template",
                description="Ad-hoc template from URL",
                git_url=args.template_url
            )
        else:
            # Select template based on requirements
            template = select_template(templates, requirements)

        print(f"\nSelected template: {template.name}")
        print(f"  {template.description}")
        print()

        # Invoke cookiecutter
        project_dir = invoke_cookiecutter(
            template,
            requirements,
            args.output_dir,
            no_cache=args.no_cache
        )

        print(f"\n✓ Project generated: {project_dir}")

        # Run post-setup
        run_post_setup(project_dir)

        # Display next steps
        print("\n" + "=" * 70)
        print("Next Steps:")
        print("=" * 70)
        print(f"  1. cd {project_dir.name}")
        print(f"  2. source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
        print(f"  3. uv run behave              # Run BDD tests")
        print(f"  4. Review features/01_foundation.feature")
        print(f"\nFor the complete BDD workflow, see BDD_IMPLEMENTATION_GUIDE.md")
        print()

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except (TemplateNotFoundError, IntegrationNotSupportedError, PrerequisiteError) as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except GitCloneError as e:
        print(f"\nGit Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
