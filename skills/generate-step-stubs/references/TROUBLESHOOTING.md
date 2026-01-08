# Troubleshooting Guide

This document covers common errors, issues, and solutions when using the `generate-step-stubs` skill.

## Table of Contents

1. [Common Errors](#common-errors)
2. [File and Path Issues](#file-and-path-issues)
3. [Parsing Issues](#parsing-issues)
4. [Generation Issues](#generation-issues)
5. [Type Inference Issues](#type-inference-issues)
6. [Integration Issues](#integration-issues)
7. [FAQ](#faq)

---

## Common Errors

### Error: File Not Found

**Symptom:**
```
✗ Error parsing features/missing.feature: Feature file not found: features/missing.feature
```

**Cause:** The specified feature file doesn't exist at the given path.

**Solutions:**
1. Verify the file path is correct:
   ```bash
   ls -la features/missing.feature
   ```
2. Check you're in the correct directory:
   ```bash
   pwd
   ```
3. Use tab completion to avoid typos:
   ```bash
   python generate_stubs.py features/<TAB>
   ```
4. Use absolute paths if relative paths aren't working:
   ```bash
   python generate_stubs.py /full/path/to/features/login.feature
   ```

---

### Error: Invalid Feature File Extension

**Symptom:**
```
✗ Error parsing myfile.txt: Expected .feature file, got: .txt
```

**Cause:** The tool only processes `.feature` files with Gherkin syntax.

**Solutions:**
1. Rename your file to have `.feature` extension:
   ```bash
   mv myfile.txt myfile.feature
   ```
2. Verify file extension:
   ```bash
   file features/login.feature
   ```
3. Ensure you're not accidentally passing non-feature files:
   ```bash
   # Wrong
   python generate_stubs.py README.md

   # Correct
   python generate_stubs.py features/*.feature
   ```

---

### Error: Output File Already Exists

**Symptom:**
```
✗ Output file login_steps.py already exists. Use -f to overwrite.
```

**Cause:** The output file already exists and `--force` flag wasn't used.

**Solutions:**
1. **Use --force flag to overwrite:**
   ```bash
   python generate_stubs.py features/login.feature -o login_steps.py --force
   ```

2. **Choose a different output path:**
   ```bash
   python generate_stubs.py features/login.feature -o login_steps_v2.py
   ```

3. **Backup existing file first:**
   ```bash
   cp login_steps.py login_steps.py.backup
   python generate_stubs.py features/login.feature -o login_steps.py --force
   ```

4. **Preview with --stdout first:**
   ```bash
   python generate_stubs.py features/login.feature --stdout | less
   ```

---

## File and Path Issues

### Steps Not Generated

**Symptom:** Feature file processed but no steps in output.

**Causes and Solutions:**

#### Cause 1: No Step Keywords Found

**Check if file contains valid step keywords:**
```bash
grep -E "^\s*(Given|When|Then|And|But)" features/myfile.feature
```

**Solution:** Ensure steps start with proper keywords:
```gherkin
# Wrong (no keywords)
Feature: Login
  Scenario: Login test
    User enters credentials
    System validates credentials
    User sees dashboard

# Correct
Feature: Login
  Scenario: Login test
    Given user enters credentials
    When system validates credentials
    Then user sees dashboard
```

#### Cause 2: Commented Out Steps

**Check for commented steps:**
```bash
cat features/myfile.feature
```

**Solution:** Remove `#` from step definitions:
```gherkin
# Wrong (commented)
  # Given a user exists
  # When the user logs in

# Correct
  Given a user exists
  When the user logs in
```

#### Cause 3: Invalid Indentation

**Solution:** Use consistent 2-space indentation:
```gherkin
# Wrong (tabs or inconsistent spacing)
Feature: Login
    Scenario: Test
Given a user

# Correct
Feature: Login
  Scenario: Test
    Given a user
```

---

### Behave Import Warning

**Symptom:**
```
Warning: behave not installed, using fallback parser
```

**Cause:** Behave package not installed, using regex-based fallback parser.

**Impact:**
- Still works but less robust parsing
- May miss some advanced Gherkin features
- Data tables and doc strings might not be detected

**Solutions:**
1. **Install behave:**
   ```bash
   uv add --dev behave
   # or
   pip install behave
   ```

2. **Verify installation:**
   ```bash
   python -c "import behave; print(behave.__version__)"
   ```

3. **Continue with fallback (not recommended):**
   - The tool will still work for basic features
   - Complex scenarios may not parse correctly

---

## Parsing Issues

### Wrong Parameter Names

**Symptom:** Generated parameter names are generic or based on literal values.

**Example:**
```gherkin
Given a user with email "alice@example.com"
```

**Generated (problematic):**
```python
@given('a user with email "{alice_example_com}"')
def a_user_with_email(context: Context, alice_example_com: str) -> None:
```

**Cause:** Parameter name is based on the literal value instead of semantic context.

**Solutions:**

1. **Manually rename parameters in generated code:**
   ```python
   @given('a user with email "{email}"')
   def a_user_with_email(context: Context, email: str) -> None:
   ```

2. **Use more generic placeholders in feature file:**
   ```gherkin
   # Instead of specific email
   Given a user with email "alice@example.com"

   # Use scenario outline
   Scenario Outline: Test with different emails
     Given a user with email "<email>"
     Examples:
       | email                |
       | alice@example.com    |
       | bob@example.com      |
   ```

3. **Known limitation:** This is a current limitation of the parameter extraction algorithm. See [IMPROVEMENTS.md](IMPROVEMENTS.md) for planned enhancements.

---

### Function Name Conflicts

**Symptom:** Multiple steps generate the same function name.

**Example:**
```gherkin
Given a user exists
Given a user exists with role admin
```

**Generated (automatic conflict resolution):**
```python
@given('a user exists')
def a_user_exists(context: Context) -> None:
    ...

@given('a user exists with role {role}')
def a_user_exists_2(context: Context, role: str) -> None:
    ...
```

**Cause:** Similar step text produces similar function names.

**Solutions:**

1. **Automatic numbering (already done):**
   - The tool automatically adds `_2`, `_3` suffixes
   - No action needed, but you may want to rename for clarity

2. **Manually rename for clarity:**
   ```python
   @given('a user exists')
   def a_basic_user_exists(context: Context) -> None:
       ...

   @given('a user exists with role {role}')
   def a_user_exists_with_role(context: Context, role: str) -> None:
       ...
   ```

3. **Refactor steps to be more specific:**
   ```gherkin
   # Instead of similar steps
   Given a user exists
   Given a user exists with role admin

   # Use one parameterized step
   Given a user with role "user"
   Given a user with role "admin"
   ```

---

## Generation Issues

### Import Errors in Generated Code

**Symptom:**
```python
from behave.runner import Context
ImportError: cannot import name 'Context' from 'behave.runner'
```

**Cause:** Old version of Behave might not export `Context` from `behave.runner`.

**Solutions:**

1. **Update Behave:**
   ```bash
   uv add --dev behave --upgrade
   # or
   pip install --upgrade behave
   ```

2. **Alternative import:**
   ```python
   # If Context import fails, use:
   from typing import Any

   def step_impl(context: Any) -> None:
       ...
   ```

3. **Check Behave version:**
   ```bash
   python -c "import behave; print(behave.__version__)"
   # Should be >= 1.2.6
   ```

---

### Syntax Errors in Generated Code

**Symptom:** Generated Python code has syntax errors.

**Check:**
```bash
python -m py_compile generated_steps.py
```

**Common Causes:**

#### Cause 1: Special Characters in Step Text

**Example:**
```gherkin
Given a string with "quotes" and 'apostrophes'
```

**Solution:** The tool should handle this, but verify generated code:
```python
@given('a string with "quotes" and \'apostrophes\'')
```

#### Cause 2: Invalid Python Identifiers

**Example:**
```gherkin
Given a step-with-hyphens
```

**Generated (should be valid):**
```python
def a_step_with_hyphens(context: Context) -> None:
```

**If invalid, report as bug.**

---

## Type Inference Issues

### Wrong Type Inferred

**Symptom:** Parameter type is incorrect.

**Example:**
```gherkin
Given a user with ID 12345
```

**Generated:**
```python
@given('a user with ID {id:d}')
def a_user_with_id(context: Context, id: int) -> None:
```

**Issue:** ID should be string (could have leading zeros or be alphanumeric).

**Solutions:**

1. **Manually fix type in generated code:**
   ```python
   @given('a user with ID {id}')
   def a_user_with_id(context: Context, id: str) -> None:
   ```

2. **Use quoted strings in feature:**
   ```gherkin
   Given a user with ID "12345"
   ```
   This will generate `str` type automatically.

3. **Semantic naming doesn't match:**
   - Current inference uses predefined name sets
   - If your domain uses different naming, manually adjust types

---

### Bool Type Not Inferred

**Symptom:** Boolean parameter typed as `str`.

**Example:**
```gherkin
Given feature is enabled
```

**Generated:**
```python
@given('feature is {enabled}')
def feature_is(context: Context, enabled: bool) -> None:
```

**Expected:** Should be `bool` (and it is if "enabled" is recognized).

**If not recognized:**

1. **Manually specify type:**
   ```python
   @given('feature is {enabled}')
   def feature_is(context: Context, enabled: str) -> None:
       # Convert inside function
       is_enabled = enabled.lower() in ('true', 'yes', 'enabled', '1')
   ```

2. **Use explicit boolean values:**
   ```gherkin
   Given feature is true
   Given feature is false
   ```

---

## Integration Issues

### Behave Doesn't Find Generated Steps

**Symptom:**
```
Undefined step: Given a user exists
```

**Causes and Solutions:**

#### Cause 1: File Location

Behave looks for steps in `features/steps/*.py`.

**Check file location:**
```bash
ls -la features/steps/
```

**Solution:** Ensure generated file is in correct location:
```bash
python generate_stubs.py features/login.feature -o features/steps/login_steps.py
```

#### Cause 2: Missing `__init__.py`

**Check:**
```bash
ls features/steps/__init__.py
```

**Solution:** Create if missing:
```bash
touch features/steps/__init__.py
```

#### Cause 3: Import Error

**Test import:**
```bash
python -c "from features.steps import login_steps"
```

**Solution:** Fix any import errors in generated code.

#### Cause 4: Pattern Mismatch

**Check patterns match exactly:**
```gherkin
# Feature file
Given a user with name "alice"

# Step definition
@given('a user with name "{name}"')  # Must match exactly
```

**Solution:** Ensure generated pattern matches Gherkin text exactly.

---

### Similarity Detection Not Working

**Symptom:** Using `--check-existing` but no similarity warnings shown.

**Causes and Solutions:**

#### Cause 1: Directory Not Found

**Check directory exists:**
```bash
ls -la features/steps/
```

**Solution:** Ensure correct path:
```bash
python generate_stubs.py features/new.feature --check-existing features/steps/
```

#### Cause 2: No Existing Steps Found

**Check for Python files:**
```bash
find features/steps/ -name "*.py" -type f
```

**If empty:** No existing steps to compare against (expected behavior).

#### Cause 3: Low Similarity

Default threshold is 60%. Steps may exist but aren't similar enough.

**Solution:** Check manually or lower threshold in code (requires modification).

---

## FAQ

### Q: Can I customize the output template?

**A:** Not currently through CLI. The template is hardcoded in `StubGenerator.TEMPLATE`.

**Workaround:**
- Edit `generate_stubs.py` directly
- Or use the generated code as a starting point and manually format

**Future:** Template customization is planned (see [IMPROVEMENTS.md](IMPROVEMENTS.md)).

---

### Q: Can I append to existing step file?

**A:** Not currently supported through CLI.

**Workaround:**
1. Generate to temporary file:
   ```bash
   python generate_stubs.py features/new.feature -o temp_steps.py
   ```

2. Manually merge:
   ```bash
   cat temp_steps.py >> features/steps/existing_steps.py
   ```

3. Remove duplicates manually

**Future:** `--append` flag is planned (see [IMPROVEMENTS.md](IMPROVEMENTS.md)).

---

### Q: How do I generate stubs only for undefined steps?

**A:** Not currently supported directly.

**Workaround:**
1. Run behave to see undefined steps:
   ```bash
   behave features/new.feature 2>&1 | grep "Undefined step"
   ```

2. Generate all steps:
   ```bash
   python generate_stubs.py features/new.feature --check-existing features/steps/
   ```

3. Only implement steps marked as undefined by behave

**Future:** `--from-behave` integration planned (see [IMPROVEMENTS.md](IMPROVEMENTS.md)).

---

### Q: Can I use this with Cucumber (non-Python)?

**A:** No, this tool generates **Python** step definitions for **Behave**.

**Alternatives:**
- For Java/Cucumber: Use IDE plugins (IntelliJ IDEA, Eclipse)
- For JavaScript: Use cucumber-js with VSCode extensions
- For Ruby: Use RubyMine or cucumber-ruby plugins

**Future:** Multi-language support is a long-term goal (see [IMPROVEMENTS.md](IMPROVEMENTS.md)).

---

### Q: What if my step has complex regex patterns?

**A:** The tool generates basic patterns. Complex regex requires manual refinement.

**Example:**
```gherkin
Given a date in format YYYY-MM-DD
```

**Generated (basic):**
```python
@given('a date in format {format}')
def a_date_in_format(context: Context, format: str) -> None:
```

**Manual refinement:**
```python
@given('a date in format {date:ti}')  # Custom type
def a_date_in_format(context: Context, date: str) -> None:
    import re
    assert re.match(r'\d{4}-\d{2}-\d{2}', date), f"Invalid date format: {date}"
```

---

### Q: How do I handle Background steps?

**A:** Background steps are automatically included in generated output.

**Note:** They're mixed with scenario steps. Future versions may separate them (see [IMPROVEMENTS.md](IMPROVEMENTS.md)).

**Workaround:** Manually organize after generation:
```python
# ============================================================================
# Background Steps
# ============================================================================

@given('the application is running')
def the_application_is_running(context: Context) -> None:
    ...

# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================
```

---

## Still Having Issues?

If you're still experiencing problems:

1. **Check Examples**: See [EXAMPLES.md](EXAMPLES.md) for working examples
2. **Review Code**: Check `scripts/generate_stubs.py` for implementation details
3. **Run Tests**: Verify your environment with included tests:
   ```bash
   pytest scripts/test_generate_stubs.py -v
   ```
4. **Check Behave Installation**:
   ```bash
   behave --version
   python -c "import behave; print(behave.__file__)"
   ```
5. **Verify Python Version**:
   ```bash
   python --version  # Should be 3.11+
   ```
6. **Review BDD Guide**: See [BDD_IMPLEMENTATION_GUIDE.md](../../../BDD_IMPLEMENTATION_GUIDE.md)

---

## Reporting Bugs

If you've found a bug:

1. Check if it's a known limitation (see main [SKILL.md](../SKILL.md))
2. Verify it's not in [IMPROVEMENTS.md](IMPROVEMENTS.md) as planned work
3. Create a minimal reproducible example:
   ```bash
   # Minimal feature file
   echo 'Feature: Test
     Scenario: Test
       Given a step' > test.feature

   # Run generator
   python generate_stubs.py test.feature --stdout
   ```
4. Report with:
   - Python version
   - Behave version (if installed)
   - Command used
   - Expected vs actual output
   - Error messages (full traceback)
