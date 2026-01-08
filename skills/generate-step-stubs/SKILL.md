---
name: generate-step-stubs
description: Auto-generates Python step definition stubs from Gherkin feature files for BDD testing with Behave. Uses Behave's parser for accurate Gherkin parsing, intelligently infers parameter types, detects existing step definitions to suggest reuse, and supports data tables and doc strings. Creates ready-to-implement step definitions with proper type hints.
license: MIT
compatibility: Requires Python 3.11+ for type hints. Requires behave for advanced parsing (falls back to regex if not available). Works with any Behave-based BDD project.
metadata:
  version: 1.1.0
  category: bdd-development
  automation_level: full
  skill_type: code_generator
---

# Generate Step Stubs

This skill automatically generates Python step definition stubs from Gherkin feature files. It's designed to accelerate the BDD development workflow by eliminating the manual work of creating step definition boilerplate.

## What's New in v1.1.0

🚀 **Major improvements** over v1.0.0:

- ✅ **Behave Parser Integration**: Uses Behave's official parser for robust Gherkin parsing (with regex fallback)
- ✅ **Intelligent Type Inference**: Automatically infers `int`, `float`, `str`, `bool` types from context and names
- ✅ **Existing Step Detection**: Scans existing step definitions and suggests reuse opportunities
- ✅ **Data Table Support**: Detects and documents steps that expect data tables
- ✅ **Doc String Support**: Detects and documents steps that expect doc strings
- ✅ **Better Type Hints**: Uses `Context` instead of `Any` for proper type checking
- ✅ **Conflict Resolution**: Handles duplicate function names with automatic numbering
- ✅ **Comprehensive Tests**: 29 unit tests covering all functionality

## When to Use This Skill

Use this skill when:

1. **Starting BDD Implementation**: You have written Gherkin feature files and need to create the corresponding step definitions
2. **Behave Reports Undefined Steps**: Running `behave` shows undefined step errors and you need stubs to implement
3. **Adding New Scenarios**: New scenarios introduce steps that don't have definitions yet
4. **Batch Generation**: You have multiple feature files and want to generate all step definitions at once
5. **Refactoring**: You're reorganizing step definitions and need a clean starting point

## What This Skill Does

The skill performs these actions automatically:

1. **Parses Gherkin Files**: Uses Behave's parser to read `.feature` files and extract all steps (including Background, Scenario Outline, data tables, and doc strings)
2. **Normalizes Steps**: Handles `Given`, `When`, `Then`, `And`, `But`, and `*` keywords
3. **Extracts Parameters**: Identifies quoted strings, numbers (int/float), and scenario outline parameters
4. **Infers Types**: Automatically determines parameter types (`int`, `float`, `str`, `bool`) from context
5. **Scans Existing Steps**: Optionally scans existing step definition files to detect similar steps
6. **Generates Patterns**: Creates Behave-compatible regex patterns with typed parameter placeholders
7. **Deduplicates**: Removes duplicate steps based on pattern matching
8. **Resolves Conflicts**: Handles duplicate function names with automatic numbering
9. **Organizes Output**: Groups step definitions by type (Given/When/Then)
10. **Creates Stubs**: Generates Python functions with proper Behave decorators and type hints

## Input Requirements

- **Feature Files**: One or more `.feature` files with valid Gherkin syntax
- **Output Location** (optional): Where to save the generated step definitions
- **Force Flag** (optional): Whether to overwrite existing files

## Output Format

The skill generates a Python file containing:

```python
"""Step definitions for {feature_name}."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('a file named "{filename}"')
def a_file_named(context: Context, filename: str) -> None:
    """TODO: Implement step: a file named "test.txt" """
    raise NotImplementedError("Step not yet implemented")

@given('a database with {count:d} records')
def a_database_with_records(context: Context, count: int) -> None:
    """TODO: Implement step: a database with 10 records"""
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('I run the command "{command}"')
def i_run_the_command(context: Context, command: str) -> None:
    """TODO: Implement step: I run the command "ls -la" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the output should contain "{text}"')
def the_output_should_contain(context: Context, text: str) -> None:
    """TODO: Implement step: the output should contain "success" """
    raise NotImplementedError("Step not yet implemented")
```

**Note the improvements:**
- ✅ Proper `Context` type instead of `Any`
- ✅ Inferred parameter types (`str`, `int`) instead of `Any`
- ✅ Cleaner function names without redundant "step_" prefix

## How to Use This Skill

### Basic Usage

```bash
# Generate stubs from a single feature file
python skills/generate-step-stubs/scripts/generate_stubs.py features/login.feature

# This creates: login_steps.py in the current directory
```

### Advanced Usage

```bash
# Specify custom output location
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    -o features/steps/login_steps.py

# Check for existing steps and suggest reuse (NEW in v1.1!)
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    --check-existing features/steps/ \
    -o features/steps/new_steps.py

# Process multiple feature files at once
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/*.feature \
    -o features/steps/all_steps.py

# Print to stdout (for piping or inspection)
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    --stdout

# Overwrite existing file
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    -o features/steps/login_steps.py \
    --force
```

### Integration with BDD Workflow

**Step 1: Write Feature File**

```gherkin
Feature: User Login
  Scenario: Successful login
    Given a user with username "alice" and password "secret123"
    When the user submits the login form
    Then the user should be redirected to the dashboard
    And a welcome message should be displayed
```

**Step 2: Generate Stubs**

```bash
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    -o features/steps/login_steps.py
```

**Step 3: Implement Steps**

Edit `features/steps/login_steps.py` and replace `NotImplementedError` with actual implementation:

```python
@given('a user with username "{username}" and password "{password}"')
def step_user_credentials(context: Any, username: str, password: str) -> None:
    """Create user with credentials."""
    context.test_user = {"username": username, "password": password}


@when('the user submits the login form')
def step_submit_login(context: Any) -> None:
    """Submit login form with test credentials."""
    from myapp.auth import login
    context.login_result = login(
        context.test_user["username"],
        context.test_user["password"]
    )


@then('the user should be redirected to the dashboard')
def step_verify_redirect(context: Any) -> None:
    """Verify redirect to dashboard."""
    assert context.login_result.redirect_url == "/dashboard"


@then('a welcome message should be displayed')
def step_verify_welcome(context: Any) -> None:
    """Verify welcome message."""
    assert "Welcome" in context.login_result.message
```

**Step 4: Run Tests**

```bash
behave features/login.feature
```

## Parameter Handling

The skill intelligently handles different parameter types **with automatic type inference**:

### Quoted Strings → `str`

**Feature:**
```gherkin
Given a file named "test.txt"
```

**Generated:**
```python
@given('a file named "{filename}"')
def a_file_named(context: Context, filename: str) -> None:
    ...
```

### Numbers → `int` or `float`

**Feature:**
```gherkin
Given a database with 10 user records
Given item costs 9.99 dollars
```

**Generated:**
```python
@given('a database with {count:d} user records')
def a_database_with_user_records(context: Context, count: int) -> None:
    ...

@given('item costs {price:f} dollars')
def item_costs_dollars(context: Context, price: float) -> None:
    ...
```

### Semantic Type Inference

The skill infers types from parameter names:

**Feature:**
```gherkin
Given a user with age 30 and price 19.99
Given feature is enabled
```

**Generated:**
```python
@given('a user with age {age:d} and price {price:f}')
def a_user_with_age_and_price(context: Context, age: int, price: float) -> None:
    ...

@given('feature is {enabled}')
def feature_is(context: Context, enabled: bool) -> None:
    ...
```

### Scenario Outline Parameters

**Feature:**
```gherkin
Scenario Outline: Test multiple values
  Given a value of <amount>

  Examples:
    | amount |
    | 100    |
    | 200    |
```

**Generated:**
```python
@given('a value of {amount}')
def a_value_of(context: Context, amount: str) -> None:
    ...
```

## Best Practices

### 1. Review Generated Stubs

Always review the generated code before implementing:
- Check parameter names make sense
- Verify automatically inferred types are correct (usually they are!)
- Check for similarity warnings suggesting existing step reuse
- Verify step patterns match your intent

### 2. Organize Step Files

Create separate step files for different feature areas:

```bash
# Generate separate files for each feature domain
python generate_stubs.py features/auth/*.feature -o features/steps/auth_steps.py
python generate_stubs.py features/data/*.feature -o features/steps/data_steps.py
python generate_stubs.py features/api/*.feature -o features/steps/api_steps.py
```

### 3. Reuse Existing Steps

Before generating new stubs:
1. Check if similar steps already exist in your step definitions
2. Consider reusing or parameterizing existing steps
3. Only generate stubs for truly new steps

### 4. Follow Naming Conventions

The skill generates function names automatically, but you should:
- Ensure they're descriptive and follow your project conventions
- Rename if needed for clarity
- Group related steps together

### 5. Verify Type Hints

Type hints are now automatically inferred! Just verify they're correct:

```python
# Automatically generated with correct types
@given('a user with age {age:d}')
def a_user_with_age(context: Context, age: int) -> None:
    ...

# If needed, you can manually override
@given('a custom parameter {value}')
def a_custom_parameter(context: Context, value: MyCustomType) -> None:
    ...
```

## Command-Line Options

```
usage: generate_stubs.py [-h] [-o OUTPUT] [--stdout] [-f] [--check-existing STEPS_DIR] feature_files [feature_files ...]

Generate Python step definition stubs from Gherkin feature files

positional arguments:
  feature_files         Path to one or more .feature files

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: feature_name_steps.py)
  --stdout              Print to stdout instead of file
  -f, --force           Overwrite output file if it exists
  --check-existing STEPS_DIR
                        Directory containing existing step definitions (enables reuse detection)
```

## Error Handling

### File Not Found

```
✗ Error parsing features/missing.feature: Feature file not found: features/missing.feature
```

**Solution**: Verify the file path is correct

### Invalid Feature File

```
✗ Error parsing myfile.txt: Expected .feature file, got: .txt
```

**Solution**: Ensure you're passing `.feature` files

### Output File Exists

```
✗ Output file login_steps.py already exists. Use -f to overwrite.
```

**Solution**: Use `--force` flag or choose a different output path

## Examples

### Example 1: Single Feature

**Input (`features/calculator.feature`):**
```gherkin
Feature: Calculator

  Scenario: Add two numbers
    Given a calculator
    When I add 5 and 3
    Then the result should be 8
```

**Command:**
```bash
python generate_stubs.py features/calculator.feature
```

**Output (`calculator_steps.py`):**
```python
@given('a calculator')
def step_a_calculator(context: Any) -> None:
    """TODO: Implement step: a calculator"""
    raise NotImplementedError("Step not yet implemented")


@when('I add {int1:d} and {int2:d}')
def step_i_add_and(context: Any, int1: Any, int2: Any) -> None:
    """TODO: Implement step: I add 5 and 3"""
    raise NotImplementedError("Step not yet implemented")


@then('the result should be {int1:d}')
def step_the_result_should_be(context: Any, int1: Any) -> None:
    """TODO: Implement step: the result should be 8"""
    raise NotImplementedError("Step not yet implemented")
```

### Example 2: Multiple Features

**Command:**
```bash
python generate_stubs.py features/auth/*.feature features/api/*.feature \
    -o features/steps/all_steps.py
```

Combines all unique steps from both feature directories into a single file.

### Example 3: Stdout for Review

**Command:**
```bash
python generate_stubs.py features/login.feature --stdout | less
```

Preview generated stubs without creating a file.

## Limitations

1. **No Semantic Understanding**: The skill generates syntactically correct stubs but doesn't understand the intent of steps
2. **No Implementation Logic**: Stubs contain `NotImplementedError` - you must implement the actual logic
3. **Basic Pattern Matching**: Complex regex patterns may need manual refinement
4. **Similarity Threshold**: Existing step detection uses 60% similarity - may miss some matches or suggest false positives

**Improvements over v1.0.0:**
- ✅ ~~Parameter Type Inference~~ - Now automatically infers `int`, `float`, `str`, `bool` types
- ✅ ~~No Existing Step Detection~~ - Now scans and suggests reuse with `--check-existing`
- ✅ ~~No data table/doc string support~~ - Now detects and documents both
- ✅ ~~Function name conflicts~~ - Now handles duplicates automatically

## Next Steps After Generation

1. **Review the Generated Code**: Check for correctness and similarity warnings
2. **Verify Type Hints**: Types are auto-inferred - just verify they're correct
3. **Consider Reusing Existing Steps**: If similarity warnings appear, consider refactoring to reuse existing steps
4. **Implement Step Logic**: Replace `NotImplementedError` with actual implementation
5. **Add Imports**: Import necessary modules and functions
6. **Test**: Run `behave` to verify your implementation
7. **Refactor**: Extract common logic into helper functions
8. **Document**: Update docstrings if needed (basic ones are generated)

## Related Skills

- **init-bdd-project**: Initialize a new BDD project structure
- **setup-behave-env**: Configure Behave environment and hooks
- **bdd-cycle**: Execute complete Red-Green-Refactor BDD cycle
- **review-gherkin-quality**: Analyze feature files for quality improvements

## Troubleshooting

### Steps Not Generated

**Symptom**: Feature file processed but no steps in output

**Cause**: Feature file may not contain valid step keywords

**Solution**: Ensure steps start with `Given`, `When`, `Then`, `And`, or `But`

### Wrong Parameter Names

**Symptom**: Generated parameter names are generic (e.g., `string1`, `int1`)

**Cause**: Step text doesn't provide semantic hints for parameters

**Solution**: Manually rename parameters to be more descriptive

### Duplicate Function Names

**Symptom**: Multiple steps generate the same function name

**Cause**: Steps have similar text patterns

**Solution**: Manually rename functions to be unique and descriptive

## Support

For issues or questions:
- Check the BDD_IMPLEMENTATION_GUIDE.md for comprehensive BDD guidance
- Review Behave documentation: https://behave.readthedocs.io/
- Examine example feature files in the project

## Version History

- **1.1.0** (2026-01-08): Major improvements
  - ✅ Integrated Behave's official parser for robust Gherkin parsing
  - ✅ Intelligent type inference for parameters (int, float, str, bool)
  - ✅ Existing step detection with similarity matching
  - ✅ Data table and doc string support detection
  - ✅ Proper Context type hints instead of Any
  - ✅ Function name conflict resolution
  - ✅ Comprehensive test suite (29 tests)
  - ✅ `--check-existing` CLI flag for reuse detection
  - ✅ Better semantic parameter naming

- **1.0.0** (2026-01-08): Initial release with core functionality
  - Gherkin parsing with regex
  - Parameter extraction for strings and numbers
  - Behave decorator generation
  - Multi-file support
  - Deduplication
  - Organized output by step type
