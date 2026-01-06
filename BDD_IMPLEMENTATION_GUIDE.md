# Universal BDD Guide: From Gherkin Specs to Working CLI

A comprehensive, framework-agnostic guide for implementing any CLI application using BDD with Gherkin specifications and Behave.

## Table of Contents

1. [Understanding the BDD Workflow](#part-1-understanding-the-bdd-workflow)
2. [Project Setup and Structure](#part-2-project-setup-and-structure)
3. [Setting Up Behave](#part-3-setting-up-behave)
4. [Writing Step Definitions](#part-4-writing-step-definitions)
5. [Implementation Strategy](#part-5-implementation-strategy)
6. [Writing Good Tests](#part-6-writing-good-tests)
7. [Common Step Patterns](#part-7-common-step-patterns)
8. [Mocking External Dependencies](#part-8-mocking-external-dependencies)
9. [Running and Debugging Tests](#part-9-running-and-debugging-tests)
10. [Continuous Integration](#part-10-continuous-integration)
11. [Complete Example Workflow](#part-11-complete-example-workflow)
12. [When to Use BDD vs Unit Tests](#part-12-when-to-use-bdd-vs-unit-tests)
13. [Measuring Success](#part-13-measuring-success)
14. [Skill Creation Strategy](#part-14-skill-creation-strategy)

---

## Part 1: Understanding the BDD Workflow

### The BDD Development Cycle

BDD follows the **Red-Green-Refactor** cycle at a higher level:

1. **Red Phase**: Write/run feature files → Step definitions fail (not implemented)
2. **Green Phase**: Implement minimal code to make tests pass
3. **Refactor Phase**: Clean up code while keeping tests green
4. **Repeat**: Move to next scenario

### The Golden Rule

**Write the minimum code necessary to make each scenario pass, then refactor.**

Never write implementation code before you have a failing test that requires it.

### Skill Creation Opportunity

**Skill: "bdd-cycle"**
- Purpose: Execute one complete Red-Green-Refactor cycle
- Input: Feature file path, scenario name
- Output: Working implementation with passing test
- Automation level: Partial (requires code review)

---

## Part 2: Project Setup and Structure

### Generic CLI Project Structure

```
cli_project/
├── src/
│   └── {project_name}/
│       ├── __init__.py
│       ├── core/                  # Domain models and business logic
│       │   ├── __init__.py
│       │   └── models.py
│       ├── infrastructure/        # External integrations
│       │   ├── __init__.py
│       │   ├── file_handler.py   # File operations
│       │   ├── api_client.py     # API integrations
│       │   └── database.py       # Database operations
│       ├── services/              # Application services
│       │   ├── __init__.py
│       │   └── processor.py      # Core processing logic
│       ├── cli/                   # CLI interface
│       │   ├── __init__.py
│       │   ├── main.py           # Entry point
│       │   └── commands.py       # Command definitions
│       └── config/                # Configuration management
│           ├── __init__.py
│           └── settings.py
├── tests/
│   ├── unit/                      # Unit tests (pytest)
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── ...
│   └── integration/               # Integration tests (pytest)
│       ├── test_api_integration.py
│       └── ...
├── features/                      # Behave BDD tests
│   ├── 01_foundation.feature
│   ├── 02_core_models.feature
│   ├── 03_file_operations.feature
│   ├── 04_external_integrations.feature
│   ├── 05_business_logic.feature
│   ├── 06_user_interface.feature
│   ├── 07_output_generation.feature
│   ├── 08_batch_operations.feature
│   ├── 09_cli_interface.feature
│   ├── 10_configuration.feature
│   ├── steps/
│   │   ├── __init__.py
│   │   ├── foundation_steps.py
│   │   ├── model_steps.py
│   │   ├── file_steps.py
│   │   ├── api_steps.py
│   │   ├── business_logic_steps.py
│   │   ├── ui_steps.py
│   │   ├── output_steps.py
│   │   ├── batch_steps.py
│   │   ├── cli_steps.py
│   │   └── config_steps.py
│   └── environment.py             # Behave hooks and setup
├── pyproject.toml
├── README.md
└── .gitignore
```

### Initial Setup Commands

```bash
# Initialize project (replace {project_name} with your project)
uv init
uv add pydantic structlog click rich pyyaml toml

# Add domain-specific dependencies as needed:
# For file processing: pypdf2, python-magic
# For APIs: httpx, anthropic, openai
# For databases: sqlalchemy, psycopg2
# For data: pandas, numpy

# Add development dependencies
uv add --dev pytest pytest-cov mypy ruff behave pytest-mock responses freezegun

# Create directory structure
PROJECT_NAME="your_project_name"
mkdir -p src/${PROJECT_NAME}/{core,infrastructure,services,cli,config}
mkdir -p tests/{unit,integration}
mkdir -p features/steps

# Initialize Python packages
touch src/${PROJECT_NAME}/__init__.py
touch src/${PROJECT_NAME}/{core,infrastructure,services,cli,config}/__init__.py
```

### Skill Creation Opportunity

**Skill: "init-bdd-project"**
- Purpose: Initialize a new BDD-based CLI project from scratch
- Input: Project name, CLI framework (click/argparse/typer), optional domain
- Output: Complete project structure with configuration files
- Automation level: Full

---

## Part 3: Setting Up Behave

### Configure Behave

Create `features/behave.ini`:

```ini
[behave]
# Show scenario outlines as individual scenarios
show_skipped = false
# Don't capture stdout
stdout_capture = false
# Show full diff on assertion failures
show_failures = true
# Stop on first failure (useful during development)
# stop = true
# Tag expression to run specific features
# tags = @wip
# Format for output
format = pretty
# Logging level
logging_level = WARNING
```

### Create Environment Setup

Create `features/environment.py`:

```python
"""Behave environment setup and teardown."""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any

def before_all(context: Any) -> None:
    """Run before all tests."""
    # Store original environment
    context.original_env = os.environ.copy()

    # Set test environment variables (customize for your CLI)
    os.environ['TEST_MODE'] = 'true'
    # Add any API keys, database URLs, etc. for testing
    # os.environ['API_KEY'] = 'test-api-key'
    # os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

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


def after_feature(context: Any, feature: Any) -> None:
    """Run after each feature."""
    # Clean up temporary directory
    if hasattr(context, 'temp_dir') and context.temp_dir.exists():
        shutil.rmtree(context.temp_dir)

    # Change back to original directory
    os.chdir(context.original_cwd)


def before_scenario(context: Any, scenario: Any) -> None:
    """Run before each scenario."""
    # Reset scenario-specific context (customize based on your domain)
    context.current_file = None
    context.result = None
    context.error = None
    context.output = None
    context.config = None
    context.process = None

    # Create scenario-specific temp directory
    context.scenario_dir = context.temp_dir / scenario.name.replace(" ", "_")
    context.scenario_dir.mkdir(exist_ok=True)
    os.chdir(context.scenario_dir)


def after_scenario(context: Any, scenario: Any) -> None:
    """Run after each scenario."""
    # Clean up scenario-specific resources
    if hasattr(context, 'client'):
        # Close any open connections
        if hasattr(context.client, 'close'):
            context.client.close()
        delattr(context, 'client')

    if hasattr(context, 'process') and context.process:
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
```

### Skill Creation Opportunity

**Skill: "setup-behave-env"**
- Purpose: Generate customized Behave environment configuration
- Input: Project domain, required integrations (API, DB, files)
- Output: Configured environment.py with appropriate hooks
- Automation level: Full

---

## Part 4: Writing Step Definitions

### Understanding Step Definitions

Step definitions are the glue between Gherkin scenarios and your code. Each Gherkin step (Given/When/Then) maps to a Python function.

### Step Definition Best Practices

1. **Keep steps focused**: One step = one action/assertion
2. **Use context object**: Store state between steps in `context`
3. **Make steps reusable**: Write generic steps that work for multiple scenarios
4. **Use step parameters**: Leverage Behave's parameter parsing
5. **Separate concerns**: Given = setup, When = action, Then = assertion

### Generic Step Definition Template

Create `features/steps/common_steps.py` for reusable steps:

```python
"""Common step definitions usable across features."""
from behave import given, when, then
from pathlib import Path
import json


# ============================================================================
# File Operations - Generic
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


@given('a {filetype} file named "{filename}"')
def step_create_typed_file(context, filetype, filename):
    """Create a file of specific type with appropriate content."""
    file_path = context.scenario_dir / filename

    # Customize based on file type
    content_map = {
        'json': '{"key": "value"}',
        'yaml': 'key: value',
        'csv': 'header1,header2\nvalue1,value2',
        'txt': 'Sample text content',
    }

    content = content_map.get(filetype.lower(), 'Default content')
    file_path.write_text(content)
    context.current_file = file_path


# ============================================================================
# Environment Variables
# ============================================================================

@given('the environment variable {var_name} is set to "{value}"')
def step_set_env_var(context, var_name, value):
    """Set an environment variable."""
    import os
    os.environ[var_name] = value


@given('the environment variable {var_name} is not set')
def step_unset_env_var(context, var_name):
    """Remove an environment variable."""
    import os
    if var_name in os.environ:
        context.original_env_vars = context.original_env_vars or {}
        context.original_env_vars[var_name] = os.environ[var_name]
        del os.environ[var_name]


# ============================================================================
# Command Execution
# ============================================================================

@when('I run the command "{command}"')
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


@when('I run the command "{command}" with input')
def step_run_command_with_input(context, command):
    """Execute a CLI command with stdin from docstring."""
    import subprocess

    try:
        result = subprocess.run(
            command.split(),
            input=context.text,
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
        f"Expected exit code 0, got {context.exit_code}\nStderr: {context.stderr}"


@then('the command should fail')
def step_command_fails(context):
    """Assert command exited with non-zero code."""
    assert context.exit_code != 0, "Expected command to fail but it succeeded"


@then('the exit code should be {code:d}')
def step_verify_exit_code(context, code):
    """Assert specific exit code."""
    assert context.exit_code == code, \
        f"Expected exit code {code}, got {context.exit_code}"


# ============================================================================
# Assertions - Output
# ============================================================================

@then('the output should contain "{text}"')
def step_output_contains(context, text):
    """Assert stdout contains specific text."""
    assert text in context.stdout, \
        f"Expected '{text}' in output:\n{context.stdout}"


@then('the output should not contain "{text}"')
def step_output_not_contains(context, text):
    """Assert stdout does not contain specific text."""
    assert text not in context.stdout, \
        f"Unexpected '{text}' found in output:\n{context.stdout}"


@then('the output should match "{pattern}"')
def step_output_matches(context, pattern):
    """Assert stdout matches regex pattern."""
    import re
    assert re.search(pattern, context.stdout), \
        f"Output does not match pattern '{pattern}':\n{context.stdout}"


@then('the error output should contain "{text}"')
def step_stderr_contains(context, text):
    """Assert stderr contains specific text."""
    assert text in context.stderr, \
        f"Expected '{text}' in stderr:\n{context.stderr}"


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


@then('the file "{filename}" should contain "{text}"')
def step_file_contains(context, filename, text):
    """Assert file contains specific text."""
    file_path = context.scenario_dir / filename
    content = file_path.read_text()
    assert text in content, f"Expected '{text}' in file {filename}"


# ============================================================================
# Assertions - JSON
# ============================================================================

@then('the output should be valid JSON')
def step_output_valid_json(context):
    """Assert stdout is valid JSON."""
    try:
        context.json_output = json.loads(context.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Output is not valid JSON: {e}\n{context.stdout}")


@then('the JSON output should have key "{key}"')
def step_json_has_key(context, key):
    """Assert JSON output contains key."""
    assert key in context.json_output, \
        f"Key '{key}' not found in JSON output: {context.json_output}"


@then('the JSON output "{key}" should be "{value}"')
def step_json_key_equals(context, key, value):
    """Assert JSON key has specific value."""
    actual = context.json_output.get(key)
    assert str(actual) == value, \
        f"Expected {key}={value}, got {key}={actual}"
```

### Skill Creation Opportunity

**Skill: "generate-step-definitions"**
- Purpose: Auto-generate step definition templates from Gherkin steps
- Input: Feature file path
- Output: Python file with step definition stubs
- Automation level: Full (with manual completion needed)

---

## Part 5: Implementation Strategy

### Universal Feature Implementation Order

For any CLI application, follow this order:

**Phase 1: Foundation**
1. Project setup and tooling
2. Core domain models
3. Configuration management

**Phase 2: Infrastructure**
4. File/data input handling
5. External integrations (APIs, databases, services)

**Phase 3: Business Logic**
6. Core processing/transformation logic
7. Validation and business rules

**Phase 4: User Interface**
8. Output generation and formatting
9. Interactive features and workflows
10. CLI interface and commands

**Phase 5: Advanced Features**
11. Batch processing and concurrency
12. Error handling and recovery
13. Logging and monitoring

### Workflow for Each Feature

#### Step 1: Organize Feature Files

```bash
# Ensure feature files are in features/ directory
# Name them clearly: NN_feature_name.feature where NN is order (01, 02, etc.)

# Tag scenarios based on implementation status:
# @wip - Work in progress (currently implementing)
# @failing - Not yet implemented
# @passing - Fully implemented and passing
# @smoke - Critical path tests
# @integration - Integration tests
```

#### Step 2: Run Behave to See Failing Steps

```bash
# Run only work-in-progress scenarios
behave --tags=@wip

# Behave will show undefined steps and provide implementation snippets
```

#### Step 3: Implement Step Definitions

Copy snippets from Behave output and implement in appropriate `steps/*.py` file.

#### Step 4: Run Tests - See Them Fail (Red)

```bash
behave --tags=@wip
# Tests fail because implementation doesn't exist yet
```

#### Step 5: Implement Minimum Code (Green)

Create the actual implementation to make tests pass.

#### Step 6: Run Tests - See Them Pass

```bash
behave --tags=@wip
# Tests should now pass!
```

#### Step 7: Refactor

Improve code quality while keeping tests green:
- Add documentation
- Improve naming
- Extract reusable functions
- Add type hints
- Improve error handling

#### Step 8: Move to Next Scenario

```bash
# Change tag from @wip to @passing
# Add @wip to next scenario
# Run all passing tests to ensure no regression
behave --tags=@passing
```

### Skill Creation Opportunity

**Skill: "implement-feature"**
- Purpose: Complete implementation of one feature (all scenarios)
- Input: Feature file path, implementation strategy
- Output: Working feature with all scenarios passing
- Automation level: Partial (requires human oversight)

---

## Part 6: Writing Good Tests

### What Makes a Good BDD Test?

**1. Declarative, Not Imperative**

❌ Bad:
```gherkin
When I call the DataProcessor constructor with config={"max_size": 100}
And I call process_data method with data from file
Then the return value should be a ProcessedData object
```

✅ Good:
```gherkin
When I process the data file
Then I should receive processed results
And the results should be valid
```

**2. Business-Focused Language**

❌ Bad:
```gherkin
When I instantiate the APIClient class
And I call the send_request method with endpoint="/users"
Then the HTTP status code should be 200
```

✅ Good:
```gherkin
When I fetch the user list
Then the request should succeed
And I should receive user data
```

**3. Test Behavior, Not Implementation**

❌ Bad:
```gherkin
Then the validator.validate() method should return True
And it should have called the check_schema() function
And the cache dictionary should contain the validation result
```

✅ Good:
```gherkin
Then the data should be valid
```

**4. One Clear Purpose Per Scenario**

❌ Bad:
```gherkin
Scenario: Test everything
  Given some data
  When I process it
  Then it should be validated
  And transformed
  And saved to database
  And sent to API
  And logged
  And cached
```

✅ Good:
```gherkin
Scenario: Process valid input data
  Given a valid data file
  When I process the file
  Then the data should be transformed correctly
  And the results should be saved
```

**5. Use Scenario Outlines for Multiple Cases**

❌ Bad:
```gherkin
Scenario: Parse JSON file
  Given a file "data.json"
  When I parse the file
  Then parsing should succeed

Scenario: Parse YAML file
  Given a file "data.yaml"
  When I parse the file
  Then parsing should succeed

Scenario: Parse CSV file
  Given a file "data.csv"
  When I parse the file
  Then parsing should succeed
```

✅ Good:
```gherkin
Scenario Outline: Parse various data formats
  Given a file named "<filename>"
  When I parse the file
  Then parsing should <result>

  Examples:
    | filename   | result  |
    | data.json  | succeed |
    | data.yaml  | succeed |
    | data.csv   | succeed |
    | data.xml   | fail    |
```

### Test Coverage Checklist

For each feature, ensure tests for:

✅ **Happy path**: Normal, expected usage
✅ **Edge cases**: Boundary values, empty inputs, maximum values
✅ **Error cases**: Invalid inputs, failures, exceptions
✅ **Validation**: Type checking, format validation, business rules
✅ **Integration**: How components work together
✅ **Configuration**: Different settings and options

### Skill Creation Opportunity

**Skill: "review-gherkin-quality"**
- Purpose: Analyze Gherkin scenarios for quality and completeness
- Input: Feature file path
- Output: Quality report with suggestions for improvement
- Automation level: Full

---

## Part 7: Common Step Patterns

### Pattern 1: Given Steps - Setup State

```python
from behave import given
from pathlib import Path
import json


@given('a configuration file with')
def step_create_config_from_docstring(context):
    """Create config file from docstring content."""
    config_path = context.scenario_dir / "config.toml"
    config_path.write_text(context.text)
    context.config_file = config_path


@given('test data')
def step_create_test_data_from_table(context):
    """Create test data from table in feature file."""
    # context.table is populated automatically by Behave
    context.test_data = []
    for row in context.table:
        context.test_data.append(dict(row))


@given('a database with {count:d} {entity_type} records')
def step_populate_database(context, count, entity_type):
    """Populate database with test records."""
    from your_project.infrastructure.database import Database

    db = Database(context.scenario_dir / "test.db")
    for i in range(count):
        db.insert(entity_type, {"id": i, "name": f"Test {i}"})
    context.database = db


@given('an API server is running on port {port:d}')
def step_start_mock_api_server(context, port):
    """Start a mock API server for testing."""
    from unittest.mock import Mock
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class MockHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

    server = HTTPServer(('localhost', port), MockHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    context.mock_server = server
```

### Pattern 2: When Steps - Perform Actions

```python
from behave import when


@when('I {action} the {resource}')
def step_generic_action(context, action, resource):
    """Generic action step - customize based on your domain."""
    # Map actions to functions
    actions = {
        'process': lambda r: context.processor.process(r),
        'validate': lambda r: context.validator.validate(r),
        'transform': lambda r: context.transformer.transform(r),
        'upload': lambda r: context.client.upload(r),
    }

    # Get the resource
    resources = {
        'file': context.current_file,
        'data': context.test_data,
        'config': context.config,
    }

    try:
        action_func = actions.get(action)
        resource_obj = resources.get(resource)
        context.result = action_func(resource_obj)
        context.error = None
    except Exception as e:
        context.result = None
        context.error = e


@when('I call the API endpoint "{endpoint}" with method {method}')
def step_api_call(context, endpoint, method):
    """Make an API call."""
    from your_project.infrastructure.api_client import APIClient

    client = APIClient()

    # Parse request body from docstring if present
    body = json.loads(context.text) if hasattr(context, 'text') else None

    try:
        response = client.request(method, endpoint, json=body)
        context.response = response
        context.status_code = response.status_code
        context.error = None
    except Exception as e:
        context.response = None
        context.error = e


@when('I import data from "{source}"')
def step_import_data(context, source):
    """Import data from various sources."""
    from your_project.services.importer import DataImporter

    importer = DataImporter()
    source_path = context.scenario_dir / source

    try:
        context.imported_data = importer.import_from(source_path)
        context.error = None
    except Exception as e:
        context.imported_data = None
        context.error = e
```

### Pattern 3: Then Steps - Assertions

```python
from behave import then


@then('the result should be {expected_result}')
def step_verify_result(context, expected_result):
    """Generic result verification."""
    assert context.error is None, f"Operation failed: {context.error}"

    # Handle different result types
    if expected_result == 'successful':
        assert context.result is not None
    elif expected_result == 'empty':
        assert not context.result
    elif expected_result.startswith('valid'):
        # Add domain-specific validation
        assert validate_result(context.result)
    else:
        assert str(context.result) == expected_result


@then('the {entity} should have {attribute} "{value}"')
def step_verify_attribute(context, entity, attribute, value):
    """Verify an entity attribute has specific value."""
    entities = {
        'result': context.result,
        'output': context.output,
        'config': context.config,
    }

    obj = entities.get(entity)
    actual_value = getattr(obj, attribute)

    # Type coercion based on actual value type
    if isinstance(actual_value, bool):
        expected_value = value.lower() == 'true'
    elif isinstance(actual_value, int):
        expected_value = int(value)
    elif isinstance(actual_value, float):
        expected_value = float(value)
    else:
        expected_value = value

    assert actual_value == expected_value, \
        f"Expected {attribute}={expected_value}, got {actual_value}"


@then('the operation should raise {exception_type}')
def step_verify_exception(context, exception_type):
    """Verify specific exception was raised."""
    assert context.error is not None, "Expected an exception but none was raised"
    assert exception_type in type(context.error).__name__, \
        f"Expected {exception_type}, got {type(context.error).__name__}"


@then('the {collection} should contain {count:d} items')
def step_verify_collection_size(context, collection, count):
    """Verify collection has specific number of items."""
    collections = {
        'results': context.result,
        'output': context.output,
        'records': context.records,
    }

    items = collections.get(collection)
    assert len(items) == count, \
        f"Expected {count} items, got {len(items)}"
```

### Pattern 4: Reusable Steps with Parameters

```python
@then('the {attribute} should be {comparison} {value}')
def step_verify_comparison(context, attribute, comparison, value):
    """Generic comparison step."""
    actual = getattr(context.result, attribute)
    expected = type(actual)(value)  # Convert to same type

    comparisons = {
        'equal to': lambda a, e: a == e,
        'greater than': lambda a, e: a > e,
        'less than': lambda a, e: a < e,
        'at least': lambda a, e: a >= e,
        'at most': lambda a, e: a <= e,
    }

    compare_func = comparisons.get(comparison)
    assert compare_func(actual, expected), \
        f"Expected {attribute} {comparison} {expected}, got {actual}"
```

### Skill Creation Opportunity

**Skill: "create-step-library"**
- Purpose: Generate a library of common step definitions for a domain
- Input: Domain type (data processing, API client, file manager, etc.)
- Output: Python module with reusable step definitions
- Automation level: Full

---

## Part 8: Mocking External Dependencies

### Why Mock?

1. **Speed**: Don't wait for real API calls, database queries, or file I/O
2. **Reliability**: Tests don't fail due to network issues or external service downtime
3. **Cost**: Don't incur charges for API usage during testing
4. **Determinism**: Same input always produces same output
5. **Coverage**: Test error cases that are hard to reproduce with real services

### Generic Mocking Patterns

#### Mocking API Calls

Create `tests/fixtures/mock_responses.py`:

```python
"""Mock responses for external services."""
from typing import Any
from unittest.mock import Mock


def mock_api_success_response(data: dict[str, Any] | None = None) -> Mock:
    """Create a successful API response mock."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = data or {"status": "success"}
    response.text = str(data)
    response.ok = True
    return response


def mock_api_error_response(status_code: int, message: str) -> Mock:
    """Create an error API response mock."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {"error": message}
    response.text = message
    response.ok = False
    response.raise_for_status.side_effect = Exception(message)
    return response


def mock_timeout_error() -> Exception:
    """Create a timeout error."""
    import requests
    return requests.Timeout("Request timed out")


def mock_connection_error() -> Exception:
    """Create a connection error."""
    import requests
    return requests.ConnectionError("Failed to connect")
```

#### Mocking File Operations

```python
"""Mock file system operations."""
from unittest.mock import mock_open, patch
from pathlib import Path


def mock_file_read(content: str):
    """Mock reading a file."""
    return mock_open(read_data=content)


def mock_file_write():
    """Mock writing to a file."""
    return mock_open()


# Usage in step definitions
@when('I read the configuration file')
def step_read_config(context):
    mock_content = """
    [settings]
    key = value
    """

    with patch('builtins.open', mock_open(read_data=mock_content)):
        from your_project.config import load_config
        context.config = load_config('config.toml')
```

#### Mocking Database Operations

```python
"""Mock database operations."""
from unittest.mock import Mock, MagicMock


def mock_database_connection():
    """Create a mock database connection."""
    conn = Mock()
    cursor = MagicMock()

    # Configure cursor behavior
    cursor.fetchall.return_value = [
        (1, 'Record 1'),
        (2, 'Record 2'),
    ]
    cursor.fetchone.return_value = (1, 'Record 1')
    cursor.rowcount = 2

    conn.cursor.return_value = cursor
    conn.commit = Mock()
    conn.rollback = Mock()

    return conn


# Usage in step definitions
@given('a database with user records')
def step_mock_database(context):
    from unittest.mock import patch

    mock_conn = mock_database_connection()

    with patch('your_project.infrastructure.database.connect', return_value=mock_conn):
        context.mock_db = mock_conn
```

### Using Mocks in Step Definitions

```python
from behave import when
from unittest.mock import patch, Mock


@when('I fetch data from the external API')
def step_fetch_from_api(context):
    """Fetch data with mocked API."""
    from tests.fixtures.mock_responses import mock_api_success_response
    from your_project.infrastructure.api_client import APIClient

    # Mock the underlying HTTP library
    with patch('httpx.get') as mock_get:
        mock_get.return_value = mock_api_success_response({
            "data": [{"id": 1, "name": "Item 1"}]
        })

        client = APIClient()
        try:
            context.result = client.fetch_data()
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e


@when('the API returns an error')
def step_api_error(context):
    """Test API error handling."""
    from tests.fixtures.mock_responses import mock_api_error_response
    from your_project.infrastructure.api_client import APIClient

    with patch('httpx.get') as mock_get:
        mock_get.return_value = mock_api_error_response(500, "Internal Server Error")

        client = APIClient()
        try:
            context.result = client.fetch_data()
            context.error = None
        except Exception as e:
            context.result = None
            context.error = e
```

### Skill Creation Opportunity

**Skill: "generate-mocks"**
- Purpose: Auto-generate mock fixtures for external dependencies
- Input: API specification (OpenAPI), database schema, or service interface
- Output: Python module with comprehensive mock fixtures
- Automation level: Full

---

## Part 9: Running and Debugging Tests

### Running Behave Tests

```bash
# Run all features
behave

# Run specific feature
behave features/03_file_operations.feature

# Run scenarios with specific tag
behave --tags=@wip           # Work in progress
behave --tags=@passing       # Passing tests
behave --tags=@smoke         # Smoke tests
behave --tags=@integration   # Integration tests

# Combine tags
behave --tags=@passing --tags=@smoke  # AND
behave --tags=@passing,@smoke         # OR
behave --tags=@passing --tags=~@slow  # NOT slow

# Run with specific format
behave --format=pretty       # Default, readable
behave --format=progress     # Simpler, dots
behave --format=json --outfile=report.json
behave --format=junit --outfile=report.xml

# Control execution
behave --stop                # Stop on first failure
behave --verbose             # Show more details
behave --no-capture          # Don't capture stdout
behave --dry-run             # Show what would run

# Run specific scenario by name
behave --name="Process valid input data"

# Run with specific tags in parallel (requires behave-parallel)
behave --tags=@passing --processes 4
```

### Debugging Failed Tests

**1. Use --verbose and --no-capture**

```bash
behave --verbose --no-capture features/05_business_logic.feature
```

**2. Add debug output in step definitions**

```python
@when('I process the data')
def step_process_data(context):
    print(f"\nDEBUG: Processing file: {context.current_file}")
    print(f"DEBUG: File size: {context.current_file.stat().st_size} bytes")

    from your_project.services.processor import DataProcessor

    processor = DataProcessor()

    try:
        result = processor.process(context.current_file)
        print(f"DEBUG: Process result: {result}")
        context.result = result
        context.error = None
    except Exception as e:
        print(f"DEBUG: Process error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        context.result = None
        context.error = e
```

**3. Use Python debugger (pdb)**

```python
@when('I process the data')
def step_process_data(context):
    import pdb; pdb.set_trace()  # Breakpoint here

    from your_project.services.processor import DataProcessor
    processor = DataProcessor()
    context.result = processor.process(context.current_file)
```

**4. Use logging**

```python
import structlog

logger = structlog.get_logger()

@when('I process the data')
def step_process_data(context):
    logger.info("processing_data", file=str(context.current_file))

    from your_project.services.processor import DataProcessor
    processor = DataProcessor()

    try:
        result = processor.process(context.current_file)
        logger.info("processing_complete", result_size=len(result))
        context.result = result
    except Exception as e:
        logger.error("processing_failed", error=str(e))
        raise
```

### Common Debugging Scenarios

**Problem: Step definition not found**
```
Undefined step: When I process the data file
```

**Solution:**
1. Check step definition exists in `features/steps/*.py`
2. Verify step text matches exactly (case-sensitive, punctuation matters)
3. Check parameters are correctly captured (e.g., `{filename}` vs `"{filename}"`)
4. Ensure step files are imported (check `__init__.py` if needed)

**Problem: Import errors**
```
ImportError: cannot import name 'DataProcessor' from 'your_project.services.processor'
```

**Solution:**
1. Verify module exists at correct path
2. Check PYTHONPATH includes `src/` directory
3. Add to `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   pythonpath = ["src"]
   ```

**Problem: Context attributes missing**
```
AttributeError: 'Context' object has no attribute 'current_file'
```

**Solution:**
1. Ensure Given steps set required attributes
2. Verify scenario execution order (Given → When → Then)
3. Initialize in `before_scenario` hook:
   ```python
   def before_scenario(context, scenario):
       context.current_file = None
       context.result = None
       context.error = None
   ```

**Problem: Flaky tests (pass sometimes, fail sometimes)**

**Solution:**
1. Check for race conditions in async code
2. Ensure test isolation (clean state between scenarios)
3. Look for time-dependent logic (use freezegun for time mocking)
4. Check external dependencies (should be mocked)

### Skill Creation Opportunity

**Skill: "debug-bdd-failure"**
- Purpose: Analyze and debug a failing BDD scenario
- Input: Feature file path, scenario name, error message
- Output: Diagnosis with suggested fixes
- Automation level: Partial (provides guidance)

---

## Part 10: Continuous Integration

### Generic CI/CD Setup with GitHub Actions

Create `.github/workflows/bdd-tests.yml`:

```yaml
name: BDD Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: uv sync

    - name: Run BDD smoke tests
      run: uv run behave --tags=@smoke --format=progress

    - name: Run all passing BDD tests
      run: uv run behave --tags=@passing --format=progress

    - name: Run unit tests with coverage
      run: |
        uv run pytest tests/unit \
          --cov=src \
          --cov-report=xml \
          --cov-report=term

    - name: Run integration tests
      run: uv run pytest tests/integration -v

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    - name: Archive test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.os }}-${{ matrix.python-version }}
        path: |
          htmlcov/
          *.xml
```

### Quality Gates

Create `.github/workflows/quality.yml`:

```yaml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: uv sync

    - name: Check code formatting
      run: uv run ruff format --check src/ tests/

    - name: Lint code
      run: uv run ruff check src/ tests/

    - name: Type checking
      run: uv run mypy src/ --strict

    - name: Check test coverage
      run: |
        uv run pytest \
          --cov=src \
          --cov-report=term \
          --cov-fail-under=90

    - name: Security check
      run: uv run bandit -r src/
```

### Skill Creation Opportunity

**Skill: "setup-ci-pipeline"**
- Purpose: Generate CI/CD configuration for BDD project
- Input: Repository hosting (GitHub/GitLab/Bitbucket), test requirements
- Output: Complete CI/CD configuration files
- Automation level: Full

---

## Part 11: Complete Example Workflow

### End-to-End Example: Building a Data Validation CLI

Let's walk through implementing a data validation feature:

#### Step 1: Write Feature File

Create `features/05_data_validation.feature`:

```gherkin
@failing
Feature: Data Validation

  As a data engineer
  I want to validate data files against schemas
  So that I can ensure data quality

  Rule: Files must match their declared schema

    @wip
    Scenario: Validate CSV file with correct schema
      Given a CSV file "users.csv" with content:
        """
        id,name,email,age
        1,Alice,alice@example.com,30
        2,Bob,bob@example.com,25
        """
      And a schema file "users_schema.json" defining:
        """
        {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "age": {"type": "integer", "minimum": 0}
          },
          "required": ["id", "name", "email"]
        }
        """
      When I run "cli-tool validate users.csv --schema users_schema.json"
      Then the command should succeed
      And the output should contain "Validation passed"
      And the output should contain "2 records validated"
```

#### Step 2: Run Behave - See Undefined Steps

```bash
behave --tags=@wip

# Output shows:
# Undefined step: Given a CSV file "users.csv" with content
# Undefined step: And a schema file "users_schema.json" defining
# Undefined step: When I run "cli-tool validate users.csv --schema users_schema.json"
```

#### Step 3: Implement Step Definitions

Create `features/steps/validation_steps.py`:

```python
from behave import given, when, then
from pathlib import Path


@given('a CSV file "{filename}" with content')
def step_create_csv_file(context, filename):
    """Create CSV file from docstring."""
    file_path = context.scenario_dir / filename
    file_path.write_text(context.text)
    context.current_file = file_path


@given('a schema file "{filename}" defining')
def step_create_schema_file(context, filename):
    """Create schema file from docstring."""
    schema_path = context.scenario_dir / filename
    schema_path.write_text(context.text)
    context.schema_file = schema_path


# Reuse existing command execution step from common_steps.py
# @when('I run "{command}"') already exists
```

#### Step 4: Run Tests - See Import Errors

```bash
behave --tags=@wip

# Output:
# Command 'cli-tool' not found
```

#### Step 5: Implement Minimum Code

Create `src/your_cli/cli/main.py`:

```python
"""CLI entry point."""
import click
from pathlib import Path


@click.group()
def cli():
    """Data validation CLI tool."""
    pass


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--schema', type=click.Path(exists=True), required=True)
def validate(file: str, schema: str):
    """Validate a data file against a schema."""
    from your_cli.services.validator import DataValidator

    validator = DataValidator()
    result = validator.validate_file(Path(file), Path(schema))

    if result.is_valid:
        click.echo(f"Validation passed")
        click.echo(f"{result.record_count} records validated")
    else:
        click.echo(f"Validation failed: {result.errors}")
        raise click.Abort()


if __name__ == '__main__':
    cli()
```

Create `src/your_cli/services/validator.py`:

```python
"""Data validation service."""
import csv
import json
from pathlib import Path
from dataclasses import dataclass
from jsonschema import validate, ValidationError


@dataclass
class ValidationResult:
    """Validation result."""
    is_valid: bool
    record_count: int
    errors: list[str]


class DataValidator:
    """Validates data files against schemas."""

    def validate_file(self, data_file: Path, schema_file: Path) -> ValidationResult:
        """
        Validate data file against schema.

        Args:
            data_file: Path to data file
            schema_file: Path to JSON schema file

        Returns:
            Validation result
        """
        # Load schema
        with open(schema_file) as f:
            schema = json.load(f)

        # Read CSV and validate each row
        errors = []
        record_count = 0

        with open(data_file) as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=1):
                # Convert types
                typed_row = self._convert_types(row)

                try:
                    validate(instance=typed_row, schema=schema)
                    record_count += 1
                except ValidationError as e:
                    errors.append(f"Row {row_num}: {e.message}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            record_count=record_count,
            errors=errors,
        )

    def _convert_types(self, row: dict[str, str]) -> dict[str, any]:
        """Convert string values to appropriate types."""
        typed_row = {}
        for key, value in row.items():
            # Try to convert to int
            try:
                typed_row[key] = int(value)
                continue
            except ValueError:
                pass

            # Try to convert to float
            try:
                typed_row[key] = float(value)
                continue
            except ValueError:
                pass

            # Keep as string
            typed_row[key] = value

        return typed_row
```

Update `pyproject.toml`:

```toml
[project.scripts]
cli-tool = "your_cli.cli.main:cli"
```

Install in development mode:

```bash
uv pip install -e .
```

#### Step 6: Run Tests - See Them Pass

```bash
behave --tags=@wip

# Output:
# Feature: Data Validation
#   Scenario: Validate CSV file with correct schema
#     Given a CSV file "users.csv" with content     # passed
#     And a schema file "users_schema.json" defining # passed
#     When I run "cli-tool validate ..."            # passed
#     Then the command should succeed               # passed
#     And the output should contain "Validation passed" # passed
#
# 1 scenario passed
```

#### Step 7: Refactor and Improve

Add error handling, logging, better type conversions, etc.:

```python
"""Data validation service - refactored."""
import csv
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import structlog
from jsonschema import validate, ValidationError, Draft7Validator

logger = structlog.get_logger()


@dataclass
class ValidationResult:
    """Validation result with detailed information."""
    is_valid: bool
    record_count: int
    errors: list[str]
    warnings: list[str] | None = None


class DataValidationError(Exception):
    """Raised when data validation configuration is invalid."""
    pass


class DataValidator:
    """
    Validates data files against JSON schemas.

    Supports CSV files with automatic type conversion and
    detailed error reporting.
    """

    def __init__(self):
        """Initialize validator."""
        self.logger = logger.bind(component="validator")

    def validate_file(
        self,
        data_file: Path,
        schema_file: Path,
        strict: bool = True,
    ) -> ValidationResult:
        """
        Validate data file against JSON schema.

        Args:
            data_file: Path to CSV data file
            schema_file: Path to JSON schema file
            strict: If True, fail on any validation error

        Returns:
            Validation result with errors and warnings

        Raises:
            DataValidationError: If schema or file format is invalid
        """
        self.logger.info(
            "starting_validation",
            data_file=str(data_file),
            schema_file=str(schema_file),
        )

        # Load and validate schema
        schema = self._load_schema(schema_file)

        # Validate data
        errors = []
        warnings = []
        record_count = 0

        with open(data_file) as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise DataValidationError("CSV file has no headers")

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                # Convert types based on schema
                typed_row = self._convert_types(row, schema)

                # Validate against schema
                validator = Draft7Validator(schema)
                row_errors = list(validator.iter_errors(typed_row))

                if row_errors:
                    for error in row_errors:
                        error_msg = f"Row {row_num}: {error.message}"
                        if strict:
                            errors.append(error_msg)
                        else:
                            warnings.append(error_msg)
                else:
                    record_count += 1

        is_valid = len(errors) == 0

        self.logger.info(
            "validation_complete",
            is_valid=is_valid,
            record_count=record_count,
            error_count=len(errors),
            warning_count=len(warnings),
        )

        return ValidationResult(
            is_valid=is_valid,
            record_count=record_count,
            errors=errors,
            warnings=warnings if not strict else None,
        )

    def _load_schema(self, schema_file: Path) -> dict[str, Any]:
        """Load and validate JSON schema."""
        try:
            with open(schema_file) as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON schema: {e}")

        # Validate schema itself
        Draft7Validator.check_schema(schema)

        return schema

    def _convert_types(
        self,
        row: dict[str, str],
        schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert string values to types specified in schema."""
        typed_row = {}
        properties = schema.get("properties", {})

        for key, value in row.items():
            if key not in properties:
                typed_row[key] = value
                continue

            expected_type = properties[key].get("type", "string")

            try:
                if expected_type == "integer":
                    typed_row[key] = int(value)
                elif expected_type == "number":
                    typed_row[key] = float(value)
                elif expected_type == "boolean":
                    typed_row[key] = value.lower() in ('true', '1', 'yes')
                else:
                    typed_row[key] = value
            except (ValueError, AttributeError):
                # Keep as string if conversion fails
                typed_row[key] = value

        return typed_row
```

#### Step 8: Add Unit Tests

Create `tests/unit/test_validator.py`:

```python
"""Unit tests for data validator."""
import pytest
from pathlib import Path
from your_cli.services.validator import DataValidator, DataValidationError


class TestDataValidator:
    """Tests for DataValidator."""

    def test_validate_valid_data(self, tmp_path):
        """Test validation of valid data."""
        # Create test files
        data_file = tmp_path / "data.csv"
        data_file.write_text("id,name\n1,Alice\n2,Bob\n")

        schema_file = tmp_path / "schema.json"
        schema_file.write_text('''{
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        }''')

        # Validate
        validator = DataValidator()
        result = validator.validate_file(data_file, schema_file)

        assert result.is_valid
        assert result.record_count == 2
        assert len(result.errors) == 0

    def test_validate_invalid_data(self, tmp_path):
        """Test validation of invalid data."""
        data_file = tmp_path / "data.csv"
        data_file.write_text("id,name\nabc,Alice\n")  # Invalid: id should be int

        schema_file = tmp_path / "schema.json"
        schema_file.write_text('''{
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        }''')

        validator = DataValidator()
        result = validator.validate_file(data_file, schema_file)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_invalid_schema(self, tmp_path):
        """Test handling of invalid schema."""
        data_file = tmp_path / "data.csv"
        data_file.write_text("id,name\n1,Alice\n")

        schema_file = tmp_path / "schema.json"
        schema_file.write_text('{"invalid": "schema"')  # Invalid JSON

        validator = DataValidator()

        with pytest.raises(DataValidationError, match="Invalid JSON schema"):
            validator.validate_file(data_file, schema_file)
```

Run unit tests:

```bash
pytest tests/unit/test_validator.py -v
```

#### Step 9: Update Feature Status

```bash
# Change @wip to @passing in feature file
# Run all passing tests to ensure no regression
behave --tags=@passing
```

### Skill Creation Opportunity

**Skill: "implement-feature-e2e"**
- Purpose: Complete end-to-end implementation of a feature from Gherkin to working code
- Input: Feature file, implementation hints
- Output: Working feature with step definitions, implementation, and unit tests
- Automation level: Partial (requires review and refinement)

---

## Part 12: When to Use BDD vs Unit Tests

### Use BDD (Behave) For:

✅ **User-facing behavior**: Features users interact with directly
✅ **Integration testing**: Multiple components working together
✅ **Acceptance criteria**: Defining when a feature is "done"
✅ **Living documentation**: Scenarios that explain how the system works
✅ **Cross-team communication**: Specs that non-technical stakeholders can read
✅ **End-to-end workflows**: Complete user journeys through the system
✅ **Regression prevention**: High-level tests that catch breaking changes

**Example BDD scenarios:**
- CLI command execution and output verification
- File processing workflows (read → transform → write)
- API integration flows (authenticate → request → handle response)
- Configuration loading and application
- Error handling and user feedback

### Use Unit Tests (pytest) For:

✅ **Implementation details**: Internal algorithms, helper functions
✅ **Edge cases**: Boundary conditions, special cases
✅ **Fast feedback**: Quick tests during development
✅ **Code coverage**: Testing all branches and paths
✅ **Refactoring safety**: Ensuring internal behavior stays correct
✅ **Performance testing**: Measuring execution time
✅ **Complex logic**: Detailed testing of business rules

**Example unit tests:**
- Data transformation functions
- Validation logic
- Parser implementations
- Utility functions
- Error handling paths
- Type conversions

### Recommended Distribution

For a typical CLI project:

```
Testing Strategy Distribution:
├── BDD Features (30-50 scenarios)          # 20% of tests, 80% of value
│   ├── CLI commands and options            # 8-12 scenarios
│   ├── Main workflows                      # 10-15 scenarios
│   ├── Integration points                  # 5-10 scenarios
│   ├── Error scenarios                     # 5-8 scenarios
│   └── Configuration                       # 2-5 scenarios
│
├── Unit Tests (200-400 tests)              # 70% of tests, detailed coverage
│   ├── Domain models                       # 30-50 tests
│   ├── Business logic                      # 50-100 tests
│   ├── Utilities and helpers               # 40-80 tests
│   ├── Validators and parsers              # 30-60 tests
│   └── Infrastructure                      # 50-110 tests
│
└── Integration Tests (20-40 tests)         # 10% of tests, critical paths
    ├── Database operations                 # 5-10 tests
    ├── API integrations                    # 5-10 tests
    ├── File system operations              # 5-10 tests
    └── External services                   # 5-10 tests
```

### The Test Pyramid

```
     /\         BDD (E2E) - Few, slow, high-level
    /  \        Examples: User workflows, CLI commands
   /----\
  / Intg  \     Integration - Some, medium, cross-component
 /--------\    Examples: API calls, database queries
/   Unit   \   Unit - Many, fast, focused
------------   Examples: Functions, classes, methods
```

### Skill Creation Opportunity

**Skill: "analyze-test-coverage"**
- Purpose: Analyze test suite and suggest improvements
- Input: Project source code, existing tests
- Output: Coverage report with gaps and recommendations
- Automation level: Full

---

## Part 13: Measuring Success

### Coverage Metrics

```bash
# BDD scenario coverage
behave --format=progress --tags=@passing
behave --dry-run  # See all scenarios without running

# Unit test coverage
pytest --cov=src --cov-report=html --cov-report=term
pytest --cov=src --cov-report=term-missing  # Show uncovered lines

# Combined coverage (run both, generate single report)
pytest --cov=src --cov-append tests/
behave --tags=@passing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Coverage by module
pytest --cov=src --cov-report=term --cov-report=annotate
```

### Quality Gates in CI

Example quality requirements:

```yaml
# .github/workflows/quality-gates.yml
- name: Enforce test coverage
  run: |
    pytest --cov=src --cov-report=term --cov-fail-under=90

- name: Enforce type coverage
  run: |
    mypy src/ --strict

- name: Enforce code quality
  run: |
    ruff check src/ --select=ALL

- name: Verify all passing scenarios
  run: |
    behave --tags=@passing --format=progress --no-capture

- name: Security scan
  run: |
    bandit -r src/ -ll

- name: Dependency audit
  run: |
    uv pip check
```

### Success Criteria Checklist

✅ **Functional**
- All `@passing` BDD scenarios pass
- All unit tests pass
- All integration tests pass
- CLI help documentation is complete
- Error messages are clear and actionable

✅ **Quality**
- 90%+ code coverage
- 100% type coverage (mypy strict mode)
- Zero linting errors (ruff)
- Zero security issues (bandit)
- No known vulnerabilities in dependencies

✅ **Documentation**
- README with installation and usage instructions
- Feature files serve as living documentation
- API documentation (if applicable)
- Configuration examples

✅ **Performance**
- CLI responds within 100ms for simple commands
- Batch operations scale linearly
- Memory usage is bounded

✅ **Usability**
- Intuitive command structure
- Helpful error messages
- Progress indicators for long operations
- Consistent output formatting

### Skill Creation Opportunity

**Skill: "generate-quality-report"**
- Purpose: Generate comprehensive quality report for project
- Input: Project directory
- Output: Report with metrics, trends, and recommendations
- Automation level: Full

---

## Part 14: Skill Creation Strategy

### Overview

Each major step in the BDD workflow can be turned into a reusable skill. Skills automate repetitive tasks while maintaining quality and consistency.

### Skill Categories and Priorities

#### 1. Project Initialization Skills (High Priority)

**init-bdd-project**
```yaml
skill_type: generator
inputs:
  - project_name: string
  - cli_framework: enum(click, argparse, typer)
  - domain: string (optional)
  - integrations: list(api, database, files)
outputs:
  - Complete directory structure
  - Configured pyproject.toml
  - Basic behave environment
  - Template feature files
automation_level: full
skill_pattern: |
  1. Create directory structure
  2. Generate pyproject.toml with dependencies
  3. Create environment.py with domain-specific setup
  4. Generate template features based on domain
  5. Create initial __init__.py files
```

**setup-behave-env**
```yaml
skill_type: generator
inputs:
  - domain: string
  - integrations: list(api, database, files, cache)
  - test_isolation_strategy: enum(per_scenario, per_feature)
outputs:
  - Customized environment.py
  - Configured behave.ini
automation_level: full
```

#### 2. Feature Development Skills (High Priority)

**generate-step-definitions**
```yaml
skill_type: code_generator
inputs:
  - feature_file_path: path
  - existing_steps: list(path) (optional)
outputs:
  - Python file with step definition stubs
  - Reuse suggestions for existing steps
automation_level: full
skill_pattern: |
  1. Parse feature file for all steps
  2. Check for existing matching step definitions
  3. Generate stubs for new steps
  4. Group by Given/When/Then
  5. Add TODO comments for implementation
```

**implement-feature**
```yaml
skill_type: workflow
inputs:
  - feature_file_path: path
  - implementation_hints: string (optional)
outputs:
  - Step definitions
  - Implementation code
  - Unit tests
  - Updated feature tags
automation_level: partial
requires: human_review
skill_pattern: |
  1. Analyze feature scenarios
  2. Generate step definitions
  3. Run tests (red)
  4. Generate minimal implementation
  5. Run tests (green)
  6. Suggest refactorings
  7. Generate unit tests
  8. Update tags to @passing
```

**bdd-cycle**
```yaml
skill_type: workflow
inputs:
  - feature_path: path
  - scenario_name: string
outputs:
  - Passing scenario
  - Implementation code
automation_level: partial
requires: human_review
skill_pattern: |
  1. Tag scenario as @wip
  2. Run behave --tags=@wip (red)
  3. Implement step definitions
  4. Run behave --tags=@wip (still red - no implementation)
  5. Implement minimal code
  6. Run behave --tags=@wip (green)
  7. Suggest refactorings
  8. Update tag to @passing
```

#### 3. Code Generation Skills (Medium Priority)

**generate-mocks**
```yaml
skill_type: code_generator
inputs:
  - api_spec: path (OpenAPI, GraphQL schema)
  - database_schema: path (SQL, ORM models)
  - service_interface: path (Python class/module)
outputs:
  - Mock fixtures module
  - Mock factory functions
  - Documentation
automation_level: full
```

**create-step-library**
```yaml
skill_type: code_generator
inputs:
  - domain: enum(cli, api_client, data_processor, file_manager)
  - custom_entities: list(string)
outputs:
  - Reusable step definitions module
  - Documentation with examples
automation_level: full
skill_pattern: |
  1. Load domain-specific step templates
  2. Customize for project entities
  3. Generate parametrized steps
  4. Add comprehensive docstrings
  5. Create usage examples
```

**implement-feature-e2e**
```yaml
skill_type: workflow
inputs:
  - feature_file: path
  - implementation_hints: string (optional)
outputs:
  - Complete working feature
automation_level: partial
requires: human_review
```

#### 4. Quality Assurance Skills (Medium Priority)

**review-gherkin-quality**
```yaml
skill_type: analyzer
inputs:
  - feature_file_path: path
outputs:
  - Quality score
  - Improvement suggestions
  - Anti-pattern warnings
automation_level: full
checks:
  - Declarative vs imperative language
  - Business focus vs implementation details
  - Scenario length and complexity
  - Reusability of steps
  - Coverage of edge cases
```

**analyze-test-coverage**
```yaml
skill_type: analyzer
inputs:
  - project_path: path
  - coverage_threshold: float (default: 0.90)
outputs:
  - Coverage report
  - Gap analysis
  - Recommendations
automation_level: full
analyzes:
  - BDD scenario coverage
  - Unit test coverage
  - Integration test coverage
  - Untested code paths
  - Missing edge cases
```

**generate-quality-report**
```yaml
skill_type: analyzer
inputs:
  - project_path: path
outputs:
  - Comprehensive quality report (markdown)
  - Trend analysis
  - Actionable recommendations
automation_level: full
includes:
  - Test coverage metrics
  - Type coverage
  - Linting results
  - Security scan results
  - Dependency audit
  - BDD scenario health
```

#### 5. Debugging and Maintenance Skills (Lower Priority)

**debug-bdd-failure**
```yaml
skill_type: debugger
inputs:
  - feature_file: path
  - scenario_name: string
  - error_message: string
outputs:
  - Diagnosis
  - Suggested fixes
  - Related code locations
automation_level: partial
diagnosis_steps:
  1. Parse error message
  2. Locate failing step definition
  3. Check implementation
  4. Analyze context setup
  5. Suggest fixes
```

#### 6. Infrastructure Skills (Lower Priority)

**setup-ci-pipeline**
```yaml
skill_type: generator
inputs:
  - repository_host: enum(github, gitlab, bitbucket)
  - test_requirements: list(string)
  - quality_gates: dict
outputs:
  - CI/CD configuration files
  - Badge markdown for README
automation_level: full
```

### Skill Implementation Approach

#### Phase 1: Manual Process Documentation
1. Document each workflow step precisely
2. Identify decision points
3. Note common pitfalls
4. Collect examples

#### Phase 2: Template Creation
1. Create parametrized templates
2. Build example library
3. Define input/output schemas
4. Document edge cases

#### Phase 3: Skill Implementation
1. Implement skill logic
2. Add validation
3. Handle errors gracefully
4. Write skill tests

#### Phase 4: Integration and Testing
1. Test skill in isolation
2. Test skill in workflow
3. Gather user feedback
4. Iterate and improve

### Skill Quality Guidelines

**Every skill should:**
- Have clear, documented inputs and outputs
- Include usage examples
- Handle errors gracefully with helpful messages
- Be idempotent (safe to run multiple times)
- Be testable
- Have a defined automation level (full/partial/guidance-only)
- Integrate with existing tools (don't reinvent)

**Automation Levels:**

- **Full**: Skill can run completely autonomously
- **Partial**: Skill automates most steps but requires human review/approval
- **Guidance**: Skill provides step-by-step instructions for human to follow

### Skill Composition

Skills can be composed into higher-level workflows:

```python
# Example: Composed workflow
def develop_new_feature(feature_description: str):
    """High-level skill composed of other skills."""

    # 1. Generate feature file from description
    feature_file = skill_generate_feature_from_description(feature_description)

    # 2. Generate step definitions
    steps_file = skill_generate_step_definitions(feature_file)

    # 3. Implement feature
    implementation = skill_implement_feature(feature_file, steps_file)

    # 4. Review quality
    quality_report = skill_review_gherkin_quality(feature_file)

    # 5. Generate tests
    unit_tests = skill_generate_unit_tests(implementation)

    # 6. Run full test suite
    test_results = skill_run_all_tests()

    return {
        "feature": feature_file,
        "implementation": implementation,
        "tests": unit_tests,
        "quality": quality_report,
        "results": test_results,
    }
```

---

## Summary: The Universal BDD Workflow

### The Complete Process

1. **Initialize Project** → Use skill: `init-bdd-project`
2. **Write Feature Files** → Use skill: `review-gherkin-quality`
3. **Generate Step Definitions** → Use skill: `generate-step-definitions`
4. **Run Tests (Red)** → `behave --tags=@wip`
5. **Implement Code (Green)** → Use skill: `implement-feature`
6. **Refactor** → Keep tests passing
7. **Add Unit Tests** → Complement BDD scenarios
8. **Review Quality** → Use skill: `analyze-test-coverage`
9. **Set Up CI/CD** → Use skill: `setup-ci-pipeline`
10. **Iterate** → Repeat for next feature

### Key Principles

✅ **Outside-In Development**: Start from user-facing behavior, work inward
✅ **Specification by Example**: Write concrete examples, not abstract requirements
✅ **Test-Driven**: Always see tests fail before implementing
✅ **Minimal Implementation**: Write just enough code to pass tests
✅ **Continuous Refactoring**: Improve code while keeping tests green
✅ **Living Documentation**: Feature files document current behavior
✅ **Shared Language**: Business and technical teams use same terminology

### Skill-Driven Development

By creating skills for each major step:
- **Reduce cognitive load**: Focus on one step at a time
- **Ensure consistency**: Follow best practices automatically
- **Speed up development**: Automate repetitive tasks
- **Improve quality**: Built-in quality checks
- **Enable collaboration**: Clear interfaces between skills

---

## Additional Resources

### Behave and BDD
- [Official Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
- [BDD by Example (Cucumber)](https://cucumber.io/docs/bdd/)
- [The Cucumber Book](https://pragprog.com/titles/hwcuc2/the-cucumber-book-second-edition/)

### Testing Best Practices
- [Test Pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Testing Strategies in Microservices](https://martinfowler.com/articles/microservice-testing/)
- [Outside-In Development](https://cucumber.io/blog/bdd/solving-how-to-organise-feature-files/)

### Python Testing Tools
- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Click Testing](https://click.palletsprojects.com/en/stable/testing/)
- [Typer Testing](https://typer.tiangolo.com/tutorial/testing/)

### CLI Development
- [Click Documentation](https://click.palletsprojects.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich (Terminal Formatting)](https://rich.readthedocs.io/)
- [Textual (TUI Framework)](https://textual.textualize.io/)

---

**This is universal BDD practice** - a framework-agnostic approach to building any CLI application with specification by example, outside-in development, and confidence that everything works together.
