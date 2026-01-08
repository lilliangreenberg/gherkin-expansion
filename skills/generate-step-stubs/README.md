# Generate Step Stubs - Quick Start Guide

Auto-generate Python step definition stubs from Gherkin feature files for Behave BDD testing.

**NEW in v1.1.0**: Intelligent type inference, existing step detection, and Behave parser integration!

## Quick Start

```bash
# Generate stubs from a feature file
python scripts/generate_stubs.py path/to/your.feature

# Save to specific location
python scripts/generate_stubs.py features/login.feature -o features/steps/login_steps.py

# Process multiple files
python scripts/generate_stubs.py features/*.feature -o features/steps/all_steps.py
```

## What It Does

1. ✅ Parses Gherkin `.feature` files using Behave's parser
2. ✅ Extracts all `Given`, `When`, `Then` steps (including Background, data tables, doc strings)
3. ✅ Intelligently infers parameter types (`int`, `float`, `str`, `bool`)
4. ✅ Detects existing steps and suggests reuse (`--check-existing`)
5. ✅ Handles parameters (quoted strings, numbers, Scenario Outline variables)
6. ✅ Removes duplicates and resolves function name conflicts
7. ✅ Generates Python stubs with proper `Context` type hints
8. ✅ Organizes by step type (Given/When/Then)

## Example

**Input (`login.feature`):**
```gherkin
Feature: User Login

  Scenario: Successful login
    Given a user with username "alice"
    When the user logs in
    Then the user should see a welcome message
```

**Command:**
```bash
python scripts/generate_stubs.py login.feature
```

**Output (`login_steps.py`):**
```python
"""Step definitions for login."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('a user with username "{username}"')
def a_user_with_username(context: Context, username: str) -> None:
    """TODO: Implement step: a user with username "alice" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('the user logs in')
def the_user_logs_in(context: Context) -> None:
    """TODO: Implement step: the user logs in"""
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the user should see a welcome message')
def the_user_should_see_a_welcome_message(context: Context) -> None:
    """TODO: Implement step: the user should see a welcome message"""
    raise NotImplementedError("Step not yet implemented")
```

**Note**: Uses `Context` type, inferred `str` for username, and cleaner function names!

## Next Steps

After generating stubs:

1. **Review** the generated code and similarity warnings
2. **Verify** type hints (already inferred automatically!)
3. **Consider reusing** existing steps if suggested
4. **Implement** the step logic (replace `NotImplementedError`)
5. **Test** with `behave`

## Command-Line Options

```
positional arguments:
  feature_files         Path to one or more .feature files

options:
  -o OUTPUT, --output OUTPUT
                        Output file path (default: feature_name_steps.py)
  --stdout              Print to stdout instead of file
  -f, --force           Overwrite output file if it exists
  --check-existing DIR  Scan directory for existing steps (suggests reuse)
  -h, --help            Show help message
```

## Requirements

- Python 3.11+
- `behave` (for advanced Gherkin parsing - optional, falls back to regex)
- No other external dependencies

## Use Cases

- **Starting BDD implementation**: Generate initial step definitions
- **Undefined steps**: Behave reports missing steps
- **Batch generation**: Multiple feature files at once
- **Refactoring**: Clean starting point for reorganization

## Tips

✅ **DO:**
- Review generated code and similarity warnings
- Use `--check-existing` to find reuse opportunities
- Verify auto-inferred types (usually correct!)
- Organize steps into logical files by domain

❌ **DON'T:**
- Use generated code without review
- Ignore similarity warnings about existing steps
- Put all steps in one massive file
- Create duplicate step definitions when reuse is possible

## Related Documentation

- Full documentation: See `SKILL.md`
- BDD workflow guide: See `../../BDD_IMPLEMENTATION_GUIDE.md`
- Behave docs: https://behave.readthedocs.io/
- Gherkin reference: https://cucumber.io/docs/gherkin/

## Troubleshooting

**No steps generated?**
- Ensure file has `.feature` extension
- Check that steps start with `Given`, `When`, `Then`, `And`, or `But`

**File exists error?**
- Use `-f` flag to overwrite
- Or choose a different output path with `-o`

**Wrong parameter names?**
- Edit the generated code to use more descriptive names

## License

MIT
