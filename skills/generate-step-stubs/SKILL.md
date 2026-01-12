---
name: generate-step-stubs
description: Auto-generates Python step definition stubs from Gherkin feature files for BDD testing with Behave. Uses Behave's parser for accurate Gherkin parsing, intelligently infers parameter types, detects existing step definitions to suggest reuse, and supports data tables and doc strings. Creates ready-to-implement step definitions with proper type hints.
license: MIT
compatibility: Requires Python 3.11+ for type hints. Requires behave for advanced parsing (falls back to regex if not available). Works with any Behave-based BDD project.
metadata:
  version: 1.2.2
  category: bdd-development
  automation_level: full
  skill_type: code_generator
---

# Generate Step Stubs

This skill automatically generates Python step definition stubs from Gherkin feature files. It's designed to accelerate the BDD development workflow by eliminating the manual work of creating step definition boilerplate.

## When to Use This Skill

Use this skill when:

1. **Starting BDD Implementation**: You have written Gherkin feature files and need to create the corresponding step definitions
2. **Behave Reports Undefined Steps**: Running `behave` shows undefined step errors and you need stubs to implement
3. **Adding New Scenarios**: New scenarios introduce steps that don't have definitions yet
4. **Batch Generation**: You have multiple feature files and want to generate all step definitions at once

## What This Skill Does

The skill performs these actions automatically:

1. **Parses Gherkin Files**: Uses Behave's parser to read `.feature` files and extract all steps
2. **Normalizes Steps**: Handles `Given`, `When`, `Then`, `And`, `But`, and `*` keywords
3. **Extracts Parameters**: Identifies quoted strings, numbers (int/Decimal/float), and scenario outline parameters
4. **Infers Types**: Automatically determines parameter types from context and naming patterns
5. **Scans Existing Steps**: Optionally scans existing step definition files to detect similar steps
6. **Generates Patterns**: Creates Behave-compatible regex patterns with typed parameter placeholders
7. **Deduplicates**: Removes duplicate steps based on pattern matching
8. **Resolves Conflicts**: Handles duplicate function names with automatic numbering
9. **Organizes Output**: Groups step definitions by type (Given/When/Then)
10. **Creates Stubs**: Generates Python functions with proper Behave decorators and type hints

## Input Requirements

- **Feature Files**: One or more `.feature` files with valid Gherkin syntax
- **Output Location** (optional): Where to save the generated step definitions
- **Existing Steps Directory** (optional): For reuse detection with `--check-existing`

## Output Format

The skill generates Python code with this structure:

```python
"""Step definitions for {feature_name}."""
from decimal import Decimal

from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('a file named "{filename}"')
def a_file_named(context: Context, filename: str) -> None:
    """TODO: Implement step: a file named "test.txt" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('I run the command "{command}"')
def i_run_the_command(context: Context, command: str) -> None:
    """TODO: Implement step: I run the command "ls" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the output should contain "{text}"')
def the_output_should_contain(context: Context, text: str) -> None:
    """TODO: Implement step: the output should contain "success" """
    raise NotImplementedError("Step not yet implemented")
```

## How to Use This Skill

### Basic Usage

```bash
# Generate stubs from a single feature file
python skills/generate-step-stubs/scripts/generate_stubs.py features/login.feature

# Specify custom output location
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    -o features/steps/login_steps.py

# Check for existing steps and suggest reuse
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    --check-existing features/steps/ \
    -o features/steps/new_steps.py

# Process multiple feature files
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/*.feature \
    -o features/steps/all_steps.py
```

### Quick Workflow

1. **Write Feature File** in Gherkin
2. **Generate Stubs**: `python generate_stubs.py features/myfeature.feature`
3. **Review Output**: Check for similarity warnings and type hints
4. **Implement Logic**: Replace `NotImplementedError` with actual code
5. **Run Tests**: `behave features/myfeature.feature`

For integration patterns and advanced workflows, see [ADVANCED_USAGE.md](references/ADVANCED_USAGE.md).

## Parameter Type Inference

The skill intelligently infers parameter types:

### From Pattern Context

```gherkin
Given a database with 10 records        → {count:d} (int)
Given item costs 9.99 dollars           → {price:f} (Decimal - monetary value)
Given latitude is 37.7749                → {latitude:f} (float - measurement)
Given a file named "test.txt"           → {filename} (str)
```

**Note**: The `:f` pattern marker indicates a floating-point number, but the **parameter name** determines whether it becomes `Decimal` (for monetary values like `price`, `cost`, `rate`) or `float` (for measurements like `latitude`, `score`, `distance`).

### From Semantic Names

```python
# Type inference based on parameter names
INT_NAMES: count, number, age, size, port, index, id
DECIMAL_NAMES: price, cost, rate, percentage, fee, tax, dollar, dollars
FLOAT_NAMES: latitude, longitude, score, ratio, distance, temperature
BOOL_NAMES: enabled, disabled, active, valid, required
```

**Example**:
```gherkin
Given a user with age 30 and price 19.99
```

**Generated**:
```python
from decimal import Decimal

@given('a user with age {age:d} and price {price:f}')
def a_user_with_age_and_price(context: Context, age: int, price: Decimal) -> None:
```

## Best Practices

### 1. Review Generated Code

Always review before implementing:
- Check parameter names are meaningful
- Verify automatically inferred types are correct
- Review similarity warnings suggesting existing step reuse
- Ensure step patterns match your intent

### 2. Organize by Domain

Create separate step files for different feature areas:

```bash
python generate_stubs.py features/auth/*.feature -o features/steps/auth_steps.py
python generate_stubs.py features/data/*.feature -o features/steps/data_steps.py
python generate_stubs.py features/api/*.feature -o features/steps/api_steps.py
```

### 3. Use Existing Step Detection

Before generating new stubs:
```bash
python generate_stubs.py features/new.feature --check-existing features/steps/
```

This scans existing steps and warns about similar patterns that could be reused.

### 4. Data Tables and Doc Strings

The skill detects and documents when steps expect additional data:

```python
@given('the following users')
def the_following_users(context: Context) -> None:
    """TODO: Implement step: the following users
    This step expects a data table in context.table"""
    raise NotImplementedError("Step not yet implemented")
```

## Command-Line Options

```
usage: generate_stubs.py [-h] [-o OUTPUT] [--stdout] [-f]
                         [--check-existing STEPS_DIR]
                         feature_files [feature_files ...]

positional arguments:
  feature_files         Path to one or more .feature files

options:
  -h, --help            Show help message
  -o OUTPUT, --output OUTPUT
                        Output file path (default: feature_name_steps.py)
  --stdout              Print to stdout instead of file
  -f, --force           Overwrite output file if it exists
  --check-existing STEPS_DIR
                        Directory containing existing step definitions
```

For complete examples, see [EXAMPLES.md](references/EXAMPLES.md).

## Limitations

1. **No Semantic Understanding**: Generates syntactically correct stubs but doesn't understand step intent
2. **No Implementation Logic**: Stubs contain `NotImplementedError` - you must implement the actual logic
3. **Basic Pattern Matching**: Complex regex patterns may need manual refinement
4. **Similarity Threshold**: Existing step detection uses 60% similarity - may miss some matches or suggest false positives

**Note**: Most limitations from v1.0.0 have been addressed:
- ✅ ~~No parameter type inference~~ - Now infers int, Decimal, float, str, bool
- ✅ ~~No existing step detection~~ - Now scans with `--check-existing`
- ✅ ~~No data table/doc string support~~ - Now detects and documents both
- ✅ ~~Function name conflicts~~ - Now handles duplicates automatically

## Next Steps After Generation

1. **Review the Generated Code**: Check for correctness and similarity warnings
2. **Verify Type Hints**: Types are auto-inferred - verify they're correct
3. **Consider Reusing Existing Steps**: If similarity warnings appear, refactor to reuse
4. **Implement Step Logic**: Replace `NotImplementedError` with actual implementation
5. **Add Imports**: Import necessary modules and functions
6. **Test**: Run `behave` to verify your implementation
7. **Refactor**: Extract common logic into helper functions

## Related Documentation

- **Extended Examples**: [EXAMPLES.md](references/EXAMPLES.md)
- **Error Handling**: [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)
- **Advanced Integration**: [ADVANCED_USAGE.md](references/ADVANCED_USAGE.md)
- **Planned Improvements**: [IMPROVEMENTS.md](references/IMPROVEMENTS.md)
- **Version History**: [CHANGELOG.md](CHANGELOG.md)

## Related Skills

- **init-bdd-project**: Initialize a new BDD project structure
- **setup-behave-env**: Configure Behave environment and hooks
- **bdd-cycle**: Execute complete Red-Green-Refactor BDD cycle
- **review-gherkin-quality**: Analyze feature files for quality improvements

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for common issues
- Review the [BDD Implementation Guide](../../BDD_IMPLEMENTATION_GUIDE.md) for comprehensive BDD guidance
- Consult Behave documentation: https://behave.readthedocs.io/
- Examine Gherkin reference: https://cucumber.io/docs/gherkin/
