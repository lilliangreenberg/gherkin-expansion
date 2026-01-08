# Fix Summary: And/But/* Step Type Inheritance

## Issue Description

**Version Affected**: v1.2.0 and earlier

**Severity**: Critical - Core functionality bug

**Problem**: And/But/* steps were incorrectly defaulting to `@given` decorator instead of inheriting the step type from the previous step in the scenario.

### Example of Incorrect Behavior

**Feature File**:
```gherkin
Feature: User Login
  Scenario: Successful login
    Given a user exists
    And the user is authenticated      # Should be @given ✓
    When the user logs in
    And the user navigates to dashboard # Was @given ✗, should be @when
    Then the user should see dashboard
    And a welcome message appears       # Was @given ✗, should be @then
```

**Before Fix (v1.2.0)**:
```python
@given('a user exists')
def a_user_exists(context: Context) -> None:
    ...

@given('the user is authenticated')  # ✓ Correct
def the_user_is_authenticated(context: Context) -> None:
    ...

@when('the user logs in')
def the_user_logs_in(context: Context) -> None:
    ...

@given('the user navigates to dashboard')  # ✗ WRONG - should be @when
def the_user_navigates_to_dashboard(context: Context) -> None:
    ...

@then('the user should see dashboard')
def the_user_should_see_dashboard(context: Context) -> None:
    ...

@given('a welcome message appears')  # ✗ WRONG - should be @then
def a_welcome_message_appears(context: Context) -> None:
    ...
```

## Root Cause

The `_convert_behave_step` method in `generate_stubs.py` (line 323-327) had hardcoded logic:

```python
step_type = behave_step.keyword.lower().strip()
if step_type in ("and", "but", "*"):
    # These inherit from context, default to 'given'
    step_type = "given"  # ✗ ALWAYS defaulted to 'given'
```

This violated the Gherkin specification which states:
> "Keywords are not taken into account when looking for a step definition"

And/But/* are syntactic sugar that should inherit the step type from **context** (the previous step), not default to a fixed type.

## Solution

Updated the parser to track the previous step type and pass it through the conversion chain:

### Changes Made

**1. Updated `_extract_steps_from_feature` method** (lines 287-318):
```python
def _extract_steps_from_feature(self, feature: Any) -> list[Step]:
    steps: list[Step] = []

    # Process Background steps
    if hasattr(feature, "background") and feature.background:
        previous_step_type: str | None = None
        for behave_step in feature.background.steps:
            step = self._convert_behave_step(behave_step, previous_step_type)
            steps.append(step)
            previous_step_type = step.step_type  # Track for next step

    # Process Scenario steps
    if hasattr(feature, "scenarios"):
        for scenario in feature.scenarios:
            if hasattr(scenario, "steps"):
                previous_step_type = None  # Reset for each scenario
                for behave_step in scenario.steps:
                    step = self._convert_behave_step(behave_step, previous_step_type)
                    steps.append(step)
                    previous_step_type = step.step_type  # Track for next step

    return self._deduplicate_steps(steps)
```

**2. Updated `_convert_behave_step` method signature** (lines 320-338):
```python
def _convert_behave_step(
    self, behave_step: Any, previous_step_type: str | None = None
) -> Step:
    """Convert Behave step to our Step dataclass.

    Args:
        behave_step: Behave Step object
        previous_step_type: Step type from previous step (for And/But/* inheritance)

    Returns:
        Step object
    """
    step_type = behave_step.keyword.lower().strip()
    if step_type in ("and", "but", "*"):
        # And/But/* inherit step type from previous step
        # If no previous step, default to 'given'
        step_type = previous_step_type if previous_step_type else "given"

    # Rest of implementation...
```

### Key Design Decisions

1. **Track per-scenario**: Reset `previous_step_type` for each new scenario
2. **Safe default**: If no previous step exists (edge case), default to 'given'
3. **Preserve existing behavior**: Background steps work the same way
4. **No breaking changes**: Only affects And/But/* steps

## Testing

### New Test Added

Added comprehensive test case `test_and_but_step_inheritance` to `test_generate_stubs.py`:

```python
def test_and_but_step_inheritance(self, tmp_path):
    """Test that And/But/* steps inherit step type from previous step."""
    # Tests all inheritance scenarios:
    # - And after Given → @given
    # - And after When → @when
    # - But after When → @when
    # - And after Then → @then
    # - But after Then → @then
```

### Test Results

**Before Fix**:
```
✗ SOME TESTS FAILED
  And after When → expected @when, got @given
  But after When → expected @when, got @given
  And after Then → expected @then, got @given
  But after Then → expected @then, got @given
```

**After Fix**:
```
✓ ALL TESTS PASSED (30/30)
  All And/But/* steps correctly inherit step type
```

## Verification

### Example Output After Fix

**Feature File**:
```gherkin
Given a user exists
And the user is authenticated
When the user logs in
And the user navigates to dashboard
But the session has not expired
Then the user should see dashboard
And a welcome message appears
But no error messages are shown
```

**Generated Output (v1.2.1)**:
```python
@given('a user exists')              # ✓ Given
@given('the user is authenticated')  # ✓ And → @given (after Given)

@when('the user logs in')            # ✓ When
@when('the user navigates to dashboard')  # ✓ And → @when (after When)
@when('the session has not expired')      # ✓ But → @when (after When)

@then('the user should see dashboard')   # ✓ Then
@then('a welcome message appears')       # ✓ And → @then (after Then)
@then('no error messages are shown')     # ✓ But → @then (after Then)
```

## Impact

### Who Is Affected

**All users** who use And/But/* keywords in their Gherkin feature files (which is the majority of BDD practitioners).

### Severity Classification

- **Functionality**: ✗ Generated incorrect decorator types
- **User Experience**: ✗ Steps would fail at runtime with confusing errors
- **Correctness**: ✗ Violated Gherkin specification
- **Severity**: **CRITICAL**

### Migration

**No migration needed** - this is a pure bug fix. Simply update to v1.2.1 and regenerate step definitions.

To verify your existing generated steps are correct:
```bash
# Regenerate your step definitions
python generate_stubs.py features/*.feature -o features/steps/regenerated.py

# Compare with existing
diff features/steps/old_steps.py features/steps/regenerated.py
```

## Files Changed

1. **generate_stubs.py**:
   - `_extract_steps_from_feature`: Added previous_step_type tracking
   - `_convert_behave_step`: Added previous_step_type parameter

2. **test_generate_stubs.py**:
   - Added `test_and_but_step_inheritance` test case
   - Test count: 29 → 30 tests

3. **CHANGELOG.md**:
   - Added v1.2.1 release notes with detailed fix description

4. **SKILL.md**:
   - Updated version to 1.2.1
   - Added "What's New in v1.2.1" section

## Compliance

This fix brings the tool into full compliance with the Gherkin specification:

> **Gherkin Reference**: "And and But can replace any of the other keywords. Keywords are not taken into account when looking for a step definition. This means you cannot have a Given, When, Then, And or But step with the same text."

The tool now correctly treats And/But/* as **contextual keywords** that inherit their semantic meaning from the previous step, rather than treating them as independent `@given` steps.

## Version Information

- **Fixed in**: v1.2.1 (2026-01-08)
- **Affected versions**: v1.0.0 - v1.2.0
- **Test suite**: 30 tests, all passing
- **Backward compatibility**: Full (only fixes broken behavior)

## Credits

- **Reported by**: Deep analysis against Gherkin specification
- **Fixed by**: Claude Code comprehensive review
- **Reviewed against**: Cucumber Gherkin Reference (https://cucumber.io/docs/gherkin/reference)
