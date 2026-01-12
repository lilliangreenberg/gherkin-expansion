# Extended Examples

This document provides comprehensive examples of using the `generate-step-stubs` skill in various scenarios.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Parameter Handling Examples](#parameter-handling-examples)
3. [Integration with BDD Workflow](#integration-with-bdd-workflow)
4. [Advanced Usage Examples](#advanced-usage-examples)

---

## Basic Examples

### Example 1: Single Feature File

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
"""Step definitions for calculator."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('a calculator')
def a_calculator(context: Context) -> None:
    """TODO: Implement step: a calculator"""
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('I add {number1:d} and {number2:d}')
def i_add_and(context: Context, number1: int, number2: int) -> None:
    """TODO: Implement step: I add 5 and 3"""
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the result should be {number1:d}')
def the_result_should_be(context: Context, number1: int) -> None:
    """TODO: Implement step: the result should be 8"""
    raise NotImplementedError("Step not yet implemented")
```

**Note**: Numbers are automatically detected and typed as `int`.

---

### Example 2: Multiple Feature Files

Combine steps from multiple features into a single output file:

**Command:**
```bash
python generate_stubs.py \
    features/auth/*.feature \
    features/api/*.feature \
    -o features/steps/all_steps.py
```

**Result:**
- Parses all `.feature` files in both directories
- Deduplicates steps across all files
- Combines into single `all_steps.py` output
- Groups by step type (Given/When/Then)

**Console Output:**
```
✓ Parsed 5 unique steps from features/auth/login.feature
✓ Parsed 3 unique steps from features/auth/logout.feature
✓ Parsed 7 unique steps from features/api/users.feature
✓ Parsed 4 unique steps from features/api/products.feature

✓ Total 15 unique steps across all files

✓ Generated step definitions: features/steps/all_steps.py
  Next steps:
  1. Review generated code and similarity warnings
  2. Update parameter types if needed (already inferred)
  3. Implement the step logic (replace NotImplementedError)
  4. Run: behave to test your implementation
```

---

### Example 3: Stdout for Review

Preview generated stubs without creating a file:

**Command:**
```bash
python generate_stubs.py features/login.feature --stdout | less
```

**Use Cases:**
- Quick preview before committing
- Piping to other tools
- Reviewing before overwriting existing file
- Generating temporary stubs for testing

**Alternative - Grep for Specific Steps:**
```bash
python generate_stubs.py features/login.feature --stdout | grep "@given"
```

---

## Parameter Handling Examples

### Quoted Strings

**Feature:**
```gherkin
Given a file named "test.txt"
When I search for "error" in the file
Then I should see "File not found"
```

**Generated:**
```python
@given('a file named "{test_txt}"')
def a_file_named(context: Context, test_txt: str) -> None:
    """TODO: Implement step: a file named "test.txt" """
    raise NotImplementedError("Step not yet implemented")

@when('I search for "{error}" in the file')
def i_search_for_in_the_file(context: Context, error: str) -> None:
    """TODO: Implement step: I search for "error" in the file"""
    raise NotImplementedError("Step not yet implemented")

@then('I should see "{file_not_found}"')
def i_should_see(context: Context, file_not_found: str) -> None:
    """TODO: Implement step: I should see "File not found" """
    raise NotImplementedError("Step not yet implemented")
```

**Note**: All quoted strings are automatically typed as `str`.

---

### Numbers (Integer, Decimal, and Float)

**Feature:**
```gherkin
Given a database with 10 user records
When I query records with limit 5
Then I should receive exactly 5 results
And the total count should be 10

Given item costs 9.99 dollars
And tax rate is 0.08
Then total price should be 10.79
```

**Generated:**
```python
from decimal import Decimal

# Integer parameters
@given('a database with {count:d} user records')
def a_database_with_user_records(context: Context, count: int) -> None:
    """TODO: Implement step: a database with 10 user records"""
    raise NotImplementedError("Step not yet implemented")

@when('I query records with limit {limit:d}')
def i_query_records_with_limit(context: Context, limit: int) -> None:
    """TODO: Implement step: I query records with limit 5"""
    raise NotImplementedError("Step not yet implemented")

# Decimal parameters for monetary values
@given('item costs {price:f} dollars')
def item_costs_dollars(context: Context, price: Decimal) -> None:
    """TODO: Implement step: item costs 9.99 dollars"""
    raise NotImplementedError("Step not yet implemented")

@given('tax rate is {rate:f}')
def tax_rate_is(context: Context, rate: Decimal) -> None:
    """TODO: Implement step: tax rate is 0.08"""
    raise NotImplementedError("Step not yet implemented")
```

**Note**:
- Integers: `10`, `5` → `{name:d}` → `int`
- Decimals (monetary): `9.99`, `0.08` (with names like price, cost, rate) → `{name:f}` → `Decimal`
- Floats (measurements): Geographic coordinates, scores → `{name:f}` → `float`

---

### Semantic Type Inference

**Feature:**
```gherkin
Given a user with age 30 and score 95.5
When server is enabled on port 8080
Then response should have status 200
```

**Generated:**
```python
from decimal import Decimal

@given('a user with age {age:d} and score {score:f}')
def a_user_with_age_and_score(context: Context, age: int, score: float) -> None:
    """TODO: Implement step: a user with age 30 and score 95.5"""
    raise NotImplementedError("Step not yet implemented")

@when('server is {enabled} on port {port:d}')
def server_is_on_port(context: Context, enabled: bool, port: int) -> None:
    """TODO: Implement step: server is enabled on port 8080"""
    raise NotImplementedError("Step not yet implemented")

@then('response should have status {status:d}')
def response_should_have_status(context: Context, status: int) -> None:
    """TODO: Implement step: response should have status 200"""
    raise NotImplementedError("Step not yet implemented")
```

**Type Inference Rules:**
- `age` → recognized as `int` (in INT_NAMES set)
- `score` → recognized as `float` (in FLOAT_NAMES set - measurement/score value)
- `enabled` → recognized as `bool` (in BOOL_NAMES set)
- `port` → recognized as `int` (in INT_NAMES set)
- `status` → recognized as `int` (in INT_NAMES set)

**Monetary vs Measurement Values:**
- Monetary (use Decimal): `price`, `cost`, `rate`, `percentage`, `fee`, `tax`, `dollar`, `dollars`
- Measurements (use float): `score`, `latitude`, `longitude`, `distance`, `temperature`, `ratio`

---

### Scenario Outline Parameters

**Feature:**
```gherkin
Scenario Outline: Test multiple values
  Given a value of <amount>
  When I multiply by <factor>
  Then the result should be <expected>

  Examples:
    | amount | factor | expected |
    | 100    | 2      | 200      |
    | 50     | 3      | 150      |
```

**Generated:**
```python
@given('a value of {amount}')
def a_value_of(context: Context, amount: str) -> None:
    """TODO: Implement step: a value of <amount>"""
    raise NotImplementedError("Step not yet implemented")

@when('I multiply by {factor}')
def i_multiply_by(context: Context, factor: str) -> None:
    """TODO: Implement step: I multiply by <factor>"""
    raise NotImplementedError("Step not yet implemented")

@then('the result should be {expected}')
def the_result_should_be(context: Context, expected: str) -> None:
    """TODO: Implement step: the result should be <expected>"""
    raise NotImplementedError("Step not yet implemented")
```

**Note**: Scenario Outline parameters (`<amount>`) are typed as `str` by default. You can manually convert inside the step implementation.

---

### Data Tables

**Feature:**
```gherkin
Given the following users:
  | username | email             | role  |
  | alice    | alice@example.com | admin |
  | bob      | bob@example.com   | user  |
```

**Generated:**
```python
@given('the following users')
def the_following_users(context: Context) -> None:
    """TODO: Implement step: the following users
    This step expects a data table in context.table"""
    raise NotImplementedError("Step not yet implemented")
```

**Implementation Example:**
```python
@given('the following users')
def the_following_users(context: Context) -> None:
    """Create users from data table."""
    context.users = []
    for row in context.table:
        user = {
            'username': row['username'],
            'email': row['email'],
            'role': row['role']
        }
        context.users.append(user)
```

---

### Doc Strings

**Feature:**
```gherkin
Given a file with content:
  """json
  {
    "name": "Alice",
    "age": 30
  }
  """
```

**Generated:**
```python
@given('a file with content')
def a_file_with_content(context: Context) -> None:
    """TODO: Implement step: a file with content
    This step expects a doc string (json) in context.text"""
    raise NotImplementedError("Step not yet implemented")
```

**Implementation Example:**
```python
@given('a file with content')
def a_file_with_content(context: Context) -> None:
    """Create file with content from doc string."""
    import json
    content = context.text
    data = json.loads(content)

    file_path = context.scenario_dir / "test_file.json"
    file_path.write_text(content)
    context.current_file = file_path
    context.file_data = data
```

---

## Integration with BDD Workflow

### Complete Example: User Login Feature

This example shows the complete workflow from Gherkin to working implementation.

#### Step 1: Write Feature File

Create `features/login.feature`:

```gherkin
Feature: User Login
  As a user
  I want to log in to the application
  So that I can access my account

  Background:
    Given the application is running
    And the database is initialized

  Scenario: Successful login with valid credentials
    Given a user with username "alice" and password "secret123"
    When the user submits the login form
    Then the user should be redirected to the dashboard
    And a welcome message should be displayed

  Scenario: Failed login with invalid password
    Given a user with username "alice" and password "secret123"
    When the user enters username "alice" and password "wrongpass"
    And the user submits the login form
    Then the login should fail
    And an error message "Invalid credentials" should be shown

  Scenario Outline: Multiple failed attempts
    Given a user with username "<username>" and password "<password>"
    When the user submits the login form
    Then the login should <result>

    Examples:
      | username | password  | result  |
      | alice    | wrong     | fail    |
      | bob      | invalid   | fail    |
      |          | secret123 | fail    |
      | alice    |           | fail    |
```

#### Step 2: Generate Step Definitions

**Command:**
```bash
python skills/generate-step-stubs/scripts/generate_stubs.py \
    features/login.feature \
    --check-existing features/steps/ \
    -o features/steps/login_steps.py
```

**Output:**
```
✓ Found 5 existing step definitions in features/steps/
✓ Parsed 10 unique steps from features/login.feature

✓ Total 10 unique steps across all files

✓ Generated step definitions: features/steps/login_steps.py
  Next steps:
  1. Review generated code and similarity warnings
  2. Update parameter types if needed (already inferred)
  3. Implement the step logic (replace NotImplementedError)
  4. Run: behave to test your implementation
```

#### Step 3: Review Generated Code

The file `features/steps/login_steps.py` contains:

```python
"""Step definitions for login."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('the application is running')
def the_application_is_running(context: Context) -> None:
    """TODO: Implement step: the application is running"""
    raise NotImplementedError("Step not yet implemented")


@given('the database is initialized')
def the_database_is_initialized(context: Context) -> None:
    """TODO: Implement step: the database is initialized"""
    raise NotImplementedError("Step not yet implemented")


@given('a user with username "{username}" and password "{password}"')
def a_user_with_username_and_password(context: Context, username: str, password: str) -> None:
    """TODO: Implement step: a user with username "alice" and password "secret123" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('the user submits the login form')
def the_user_submits_the_login_form(context: Context) -> None:
    """TODO: Implement step: the user submits the login form"""
    raise NotImplementedError("Step not yet implemented")


@when('the user enters username "{username}" and password "{password}"')
def the_user_enters_username_and_password(context: Context, username: str, password: str) -> None:
    """TODO: Implement step: the user enters username "alice" and password "wrongpass" """
    raise NotImplementedError("Step not yet implemented")


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the user should be redirected to the dashboard')
def the_user_should_be_redirected_to_the_dashboard(context: Context) -> None:
    """TODO: Implement step: the user should be redirected to the dashboard"""
    raise NotImplementedError("Step not yet implemented")


@then('a welcome message should be displayed')
def a_welcome_message_should_be_displayed(context: Context) -> None:
    """TODO: Implement step: a welcome message should be displayed"""
    raise NotImplementedError("Step not yet implemented")


@then('the login should fail')
def the_login_should_fail(context: Context) -> None:
    """TODO: Implement step: the login should fail"""
    raise NotImplementedError("Step not yet implemented")


@then('an error message "{message}" should be shown')
def an_error_message_should_be_shown(context: Context, message: str) -> None:
    """TODO: Implement step: an error message "Invalid credentials" should be shown"""
    raise NotImplementedError("Step not yet implemented")


@then('the login should {result}')
def the_login_should(context: Context, result: str) -> None:
    """TODO: Implement step: the login should fail"""
    raise NotImplementedError("Step not yet implemented")
```

#### Step 4: Implement Step Logic

Replace `NotImplementedError` with actual implementation:

```python
"""Step definitions for login."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

@given('the application is running')
def the_application_is_running(context: Context) -> None:
    """Start the application."""
    from myapp import create_app
    context.app = create_app(testing=True)
    context.client = context.app.test_client()


@given('the database is initialized')
def the_database_is_initialized(context: Context) -> None:
    """Initialize test database."""
    from myapp.database import init_db, clear_db
    clear_db()
    init_db()


@given('a user with username "{username}" and password "{password}"')
def a_user_with_username_and_password(context: Context, username: str, password: str) -> None:
    """Create a test user with credentials."""
    from myapp.models import User
    from myapp.database import db

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    context.test_user = {'username': username, 'password': password}


# ============================================================================
# When Steps - Actions and Events
# ============================================================================

@when('the user submits the login form')
def the_user_submits_the_login_form(context: Context) -> None:
    """Submit login form with test user credentials."""
    response = context.client.post('/login', data={
        'username': context.test_user['username'],
        'password': context.test_user['password']
    })
    context.login_response = response


@when('the user enters username "{username}" and password "{password}"')
def the_user_enters_username_and_password(context: Context, username: str, password: str) -> None:
    """Override test user credentials."""
    context.test_user = {'username': username, 'password': password}


# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

@then('the user should be redirected to the dashboard')
def the_user_should_be_redirected_to_the_dashboard(context: Context) -> None:
    """Verify redirect to dashboard."""
    assert context.login_response.status_code == 302
    assert '/dashboard' in context.login_response.location


@then('a welcome message should be displayed')
def a_welcome_message_should_be_displayed(context: Context) -> None:
    """Verify welcome message in response."""
    response = context.client.get(context.login_response.location)
    assert b'Welcome' in response.data


@then('the login should fail')
def the_login_should_fail(context: Context) -> None:
    """Verify login failed."""
    assert context.login_response.status_code in (401, 403)


@then('an error message "{message}" should be shown')
def an_error_message_should_be_shown(context: Context, message: str) -> None:
    """Verify specific error message."""
    assert message.encode() in context.login_response.data


@then('the login should {result}')
def the_login_should(context: Context, result: str) -> None:
    """Verify login result (success/fail)."""
    if result == 'fail':
        assert context.login_response.status_code in (401, 403)
    elif result == 'succeed':
        assert context.login_response.status_code in (200, 302)
```

#### Step 5: Run Tests

```bash
behave features/login.feature --format=pretty
```

**Expected Output:**
```
Feature: User Login

  Background:
    Given the application is running         # passed
    And the database is initialized          # passed

  Scenario: Successful login with valid credentials
    Given a user with username "alice" and password "secret123"  # passed
    When the user submits the login form     # passed
    Then the user should be redirected to the dashboard  # passed
    And a welcome message should be displayed  # passed

  Scenario: Failed login with invalid password
    Given a user with username "alice" and password "secret123"  # passed
    When the user enters username "alice" and password "wrongpass"  # passed
    And the user submits the login form      # passed
    Then the login should fail               # passed
    And an error message "Invalid credentials" should be shown  # passed

  Scenario Outline: Multiple failed attempts -- @1.1
    Given a user with username "alice" and password "wrong"  # passed
    When the user submits the login form     # passed
    Then the login should fail               # passed

  (3 more scenario outline examples...)

5 scenarios (5 passed)
25 steps (25 passed)
0m2.134s
```

---

## Advanced Usage Examples

### Checking for Existing Steps

**Scenario**: You're adding a new feature and want to avoid duplicating existing steps.

**Command:**
```bash
python generate_stubs.py \
    features/new_feature.feature \
    --check-existing features/steps/ \
    -o features/steps/new_feature_steps.py
```

**Output with Similarity Warnings:**
```python
@given('a user with name "{name}"')
def a_user_with_name(context: Context, name: str) -> None:
    """TODO: Implement step: a user with name "alice"

    NOTE: Similar step exists in auth_steps.py:42
    Pattern: a user with username "{username}"
    Consider reusing or refactoring.
    """
    raise NotImplementedError("Step not yet implemented")
```

**Recommendation**: Refactor to use existing step instead of creating a duplicate.

---

### Processing Multiple Features by Domain

**Organize by feature domain:**

```bash
# Authentication steps
python generate_stubs.py \
    features/auth/*.feature \
    -o features/steps/auth_steps.py

# API steps
python generate_stubs.py \
    features/api/*.feature \
    -o features/steps/api_steps.py

# Data processing steps
python generate_stubs.py \
    features/data/*.feature \
    -o features/steps/data_steps.py
```

**Benefits:**
- Clear organization
- Easier to maintain
- Reduced merge conflicts
- Domain-specific step libraries

---

### Preview Before Committing

**Quick preview with syntax highlighting:**

```bash
python generate_stubs.py features/new.feature --stdout | bat -l python
```

**Or with grep to find specific steps:**

```bash
# Find all Given steps
python generate_stubs.py features/*.feature --stdout | grep -A 3 "@given"

# Find steps with parameters
python generate_stubs.py features/*.feature --stdout | grep -E '\{[^}]+\}'
```

---

## Summary

These examples demonstrate:
- ✅ Basic single-file and multi-file usage
- ✅ Parameter handling (strings, numbers, semantic types)
- ✅ Data tables and doc strings
- ✅ Complete BDD workflow integration
- ✅ Existing step detection
- ✅ Domain-based organization
- ✅ Preview and inspection techniques

For troubleshooting common issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

For advanced integration patterns, see [ADVANCED_USAGE.md](ADVANCED_USAGE.md).
