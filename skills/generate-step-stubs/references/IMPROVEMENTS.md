# Recommended Improvements for generate-step-stubs

## Quick Win: Use Behave's Built-in Parser

Instead of regex-based line parsing, use Behave's parser:

```python
from behave.parser import parse_file
from behave.model import Step as BehaveStep

class GherkinParser:
    def parse_file(self, file_path: Path) -> list[Step]:
        """Parse using Behave's parser."""
        feature = parse_file(str(file_path))
        steps = []

        # Process Background steps
        if feature.background:
            for behave_step in feature.background.steps:
                steps.append(self._convert_behave_step(behave_step))

        # Process Scenario steps
        for scenario in feature.scenarios:
            for behave_step in scenario.steps:
                step = self._convert_behave_step(behave_step)

                # Handle data tables
                if behave_step.table:
                    step.has_table = True
                    step.table_headers = behave_step.table.headings

                # Handle doc strings
                if behave_step.text:
                    step.has_docstring = True
                    step.docstring_content_type = behave_step.text.content_type

                steps.append(step)

        return self._deduplicate_steps(steps)

    def _convert_behave_step(self, behave_step: BehaveStep) -> Step:
        """Convert Behave step to our Step dataclass."""
        pattern, params = self._extract_parameters(behave_step.name)
        return Step(
            step_type=behave_step.keyword.lower().strip(),
            text=behave_step.name,
            pattern=pattern,
            params=params,
            has_table=behave_step.table is not None,
            has_docstring=behave_step.text is not None,
        )
```

## Quick Win: Detect Existing Steps

```python
import ast
from typing import NamedTuple

class ExistingStepDef(NamedTuple):
    """Represents an existing step definition."""
    step_type: str
    pattern: str
    function_name: str
    file_path: Path
    line_number: int

class ExistingStepScanner:
    """Scans for existing step definitions."""

    def scan_directory(self, steps_dir: Path) -> list[ExistingStepDef]:
        """Scan all Python files in steps directory."""
        existing_steps = []

        for py_file in steps_dir.glob("**/*.py"):
            if py_file.name.startswith("_"):
                continue

            existing_steps.extend(self._parse_file(py_file))

        return existing_steps

    def _parse_file(self, file_path: Path) -> list[ExistingStepDef]:
        """Parse a Python file for step definitions."""
        steps = []

        try:
            tree = ast.parse(file_path.read_text())
        except SyntaxError:
            return steps

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for @given/@when/@then decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'id'):
                            decorator_name = decorator.func.id
                            if decorator_name in ('given', 'when', 'then'):
                                # Extract pattern from first argument
                                if decorator.args:
                                    pattern_node = decorator.args[0]
                                    if isinstance(pattern_node, ast.Constant):
                                        pattern = pattern_node.value
                                        steps.append(ExistingStepDef(
                                            step_type=decorator_name,
                                            pattern=pattern,
                                            function_name=node.name,
                                            file_path=file_path,
                                            line_number=node.lineno,
                                        ))

        return steps

    def find_similar_steps(
        self,
        new_step: Step,
        existing_steps: list[ExistingStepDef],
        threshold: float = 0.7
    ) -> list[ExistingStepDef]:
        """Find existing steps similar to new step."""
        from difflib import SequenceMatcher

        similar = []
        for existing in existing_steps:
            if existing.step_type != new_step.step_type:
                continue

            # Compare patterns
            similarity = SequenceMatcher(
                None,
                new_step.pattern.lower(),
                existing.pattern.lower()
            ).ratio()

            if similarity >= threshold:
                similar.append((similarity, existing))

        # Sort by similarity (highest first)
        similar.sort(reverse=True, key=lambda x: x[0])
        return [step for _, step in similar]
```

## Quick Win: Better Type Inference

```python
from behave.runner import Context

class TypeInferencer:
    """Infer parameter types from patterns and names."""

    INT_NAMES = {
        'count', 'number', 'num', 'age', 'size', 'length',
        'quantity', 'amount', 'total', 'index', 'id'
    }

    FLOAT_NAMES = {
        'price', 'cost', 'rate', 'percentage', 'ratio',
        'latitude', 'longitude', 'score', 'value'
    }

    BOOL_NAMES = {
        'enabled', 'disabled', 'active', 'inactive', 'valid',
        'invalid', 'required', 'optional', 'success', 'failure'
    }

    def infer_type(self, param_name: str, pattern_context: str) -> str:
        """
        Infer Python type for a parameter.

        Args:
            param_name: Name of the parameter
            pattern_context: The pattern containing the parameter

        Returns:
            Python type annotation string
        """
        # Check pattern for explicit type hints
        if f'{{{param_name}:d}}' in pattern_context:
            return 'int'
        elif f'{{{param_name}:f}}' in pattern_context:
            return 'float'
        elif f'{{{param_name}:w}}' in pattern_context:
            return 'str'  # Word
        elif f'"{{{param_name}}}"' in pattern_context:
            return 'str'  # Quoted

        # Semantic inference from name
        clean_name = param_name.lower().strip('_')

        if clean_name in self.INT_NAMES:
            return 'int'
        elif clean_name in self.FLOAT_NAMES:
            return 'float'
        elif clean_name in self.BOOL_NAMES:
            return 'bool'

        # Default to str
        return 'str'

    def get_context_type(self) -> str:
        """Return proper context type annotation."""
        return 'Context'  # from behave.runner import Context

# Usage in generator:
inferencer = TypeInferencer()

params_str = ", ".join(
    f"{param}: {inferencer.infer_type(param, step.pattern)}"
    for param in step.params
)
```

## Structural Improvements

### Split Documentation

Move to progressive disclosure:

```
generate-step-stubs/
├── SKILL.md                          # Core documentation (150 lines)
├── README.md                         # Quick start
├── references/
│   ├── EXAMPLES.md                   # Extended examples
│   ├── TROUBLESHOOTING.md           # Common issues
│   ├── ADVANCED_USAGE.md            # Multi-file, templates
│   ├── IMPROVEMENTS.md              # This file
│   └── INTEGRATION_GUIDE.md         # CI/CD, hooks
├── assets/
│   └── example_features/
│       ├── simple.feature
│       ├── with_tables.feature
│       ├── with_docstrings.feature
│       └── scenario_outline.feature
└── scripts/
    ├── generate_stubs.py
    └── test_generate_stubs.py       # Add tests!
```

### Add Unit Tests

```python
# scripts/test_generate_stubs.py
import pytest
from pathlib import Path
from generate_stubs import GherkinParser, StubGenerator, Step

def test_parse_simple_feature():
    """Test parsing a simple feature file."""
    parser = GherkinParser()
    content = """
    Feature: Login
      Scenario: Successful login
        Given a user with username "alice"
        When the user logs in
        Then the user should see welcome message
    """
    steps = parser.parse_content(content)

    assert len(steps) == 3
    assert steps[0].step_type == "given"
    assert steps[0].pattern == 'a user with username "{username}"'
    assert steps[0].params == ["username"]

def test_parameter_extraction():
    """Test parameter extraction from steps."""
    parser = GherkinParser()

    # Quoted strings
    pattern, params = parser._extract_parameters('a file named "test.txt"')
    assert pattern == 'a file named "{file}"'
    assert params == ["file"]

    # Numbers
    pattern, params = parser._extract_parameters('a database with 10 records')
    assert pattern == 'a database with {count:d} records'
    assert params == ["count"]

def test_deduplication():
    """Test step deduplication."""
    parser = GherkinParser()
    steps = [
        Step("given", "a user", "a user", []),
        Step("given", "a user", "a user", []),  # Duplicate
        Step("when", "I login", "I login", []),
    ]
    parser.steps = steps
    unique = parser._deduplicate_steps()

    assert len(unique) == 2

def test_function_name_generation():
    """Test function name generation."""
    generator = StubGenerator()

    step = Step("given", 'a file named "test"', 'a file named "{name}"', ["name"])
    name = generator._generate_function_name(step)

    assert name == "a_file_named"
    assert name.isidentifier()  # Valid Python identifier
```

## CLI Enhancements

### Add New Options

```bash
# Existing step detection
python generate_stubs.py features/login.feature \
    --check-existing features/steps/ \
    --suggest-reuse

# Output organization
python generate_stubs.py features/*.feature \
    --split-by-feature \
    --output-dir features/steps/

# Append to existing file
python generate_stubs.py features/new.feature \
    --append features/steps/all_steps.py

# Integration with behave
python generate_stubs.py \
    --from-behave features/ \
    --only-undefined

# Preview mode
python generate_stubs.py features/*.feature \
    --preview

# Custom templates
python generate_stubs.py features/api.feature \
    --template templates/api_steps.py.jinja2
```

## Integration Examples

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: update-step-stubs
        name: Update BDD step stubs
        entry: python skills/generate-step-stubs/scripts/generate_stubs.py
        args: [
          'features/*.feature',
          '--check-existing', 'features/steps/',
          '--preview'  # Just warn, don't generate
        ]
        language: python
        files: \.feature$
```

### CI/CD Integration

```yaml
# .github/workflows/bdd-checks.yml
name: BDD Step Coverage

on: [push, pull_request]

jobs:
  check-steps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for undefined steps
        run: |
          python skills/generate-step-stubs/scripts/generate_stubs.py \
            features/*.feature \
            --check-existing features/steps/ \
            --report-missing \
            --fail-if-undefined
```

## Template Customization Example

```python
# templates/custom_steps.py.jinja2
"""Step definitions for {{ feature_name }}.

Auto-generated on {{ generation_date }}.
Review and implement the steps below.
"""
from behave import given, when, then
from behave.runner import Context
import structlog

from myproject.testing.helpers import (
    setup_test_context,
    cleanup_test_context,
)

logger = structlog.get_logger(__name__)


{% for step in given_steps %}
@given('{{ step.pattern }}')
def {{ step.function_name }}(
    context: Context
    {%- for param in step.params -%}
    , {{ param }}: {{ step.param_types[param] }}
    {%- endfor -%}
) -> None:
    """{{ step.text }}

    {% if step.has_table %}
    This step expects a data table.
    {% endif %}
    {% if step.has_docstring %}
    This step expects a doc string.
    {% endif %}

    TODO: Implement this step
    """
    logger.info(
        "step_execution",
        step_type="given",
        pattern="{{ step.pattern }}",
        {% for param in step.params -%}
        {{ param }}={{ param }},
        {% endfor %}
    )
    raise NotImplementedError("Step '{{ step.text }}' not yet implemented")

{% endfor %}
```

## Future Enhancements

### v2.0 Features
- [ ] AI-powered step implementation suggestions
- [ ] Integration with Claude Code for automatic implementation
- [ ] Step definition refactoring tool
- [ ] Visual step coverage dashboard
- [ ] Multi-language support (Java, JavaScript, Ruby)
- [ ] Gherkin linting and formatting
- [ ] Step performance profiling
- [ ] Automatic test data generation

### Integration with Other Skills
- `init-bdd-project`: Auto-generate stubs after project init
- `review-gherkin-quality`: Run quality checks during generation
- `bdd-cycle`: Integrate stub generation into Red-Green-Refactor workflow
