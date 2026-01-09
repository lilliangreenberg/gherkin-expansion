# Changelog

## [1.2.2] - 2026-01-09

### 🐛 Bug Fixes

#### Critical: Fixed Rule Block Support in Gherkin Parser

**Problem**: Feature files using Gherkin `Rule:` blocks were incorrectly reporting "No steps found" even when they contained valid scenarios with steps.

**Example of affected feature** (data_export.feature):
```gherkin
Feature: Data Export
  Rule: Export must support multiple file formats
    Scenario: Export to CSV
      Given I have a dataset with 100 records
      When I export to CSV format
      Then a CSV file should be generated
```

**Root Cause**: The `_extract_steps_from_feature` method only processed `feature.scenarios` but didn't handle scenarios nested under `Rule:` blocks. When a feature uses Rules to organize scenarios, `feature.scenarios` is empty and the actual scenarios are in `feature.rules[].scenarios`.

**Fix**: Updated parser to:
1. Process top-level scenarios from `feature.scenarios`
2. Process scenarios nested under `feature.rules`
3. Support Rule-level backgrounds (in addition to Feature-level backgrounds)
4. Maintain proper step type inheritance within Rule scenarios

**Impact**: Feature files using Rules now work correctly. Tested with:
- `data_export.feature`: 144 steps extracted (was 0)
- `notification_system.feature`: 121 steps extracted (was 0)
- `search_functionality.feature`: 139 steps extracted (was 0)
- `shopping_cart.feature`: 108 steps extracted (was 0)
- `user_authentication.feature`: 70 steps extracted (was 0)

**Testing**: Verified all feature files in `gherkin-examples/` directory now parse correctly.

**Files Changed**:
- `generate_stubs.py`: Updated `_extract_steps_from_feature` to iterate through `feature.rules`

**Note**: Rules are a Gherkin feature for organizing scenarios by business rules. This is a commonly used pattern in BDD and is now fully supported.

---

## [1.2.1] - 2026-01-08

### 🐛 Bug Fixes

#### Critical: Fixed And/But/* Step Type Inheritance

**Problem**: And/But/* steps were incorrectly defaulting to `@given` decorator instead of inheriting the step type from the previous step.

**Example of incorrect behavior** (v1.2.0 and earlier):
```gherkin
When the user logs in
And the user navigates to dashboard  # Was incorrectly @given, should be @when
```

**Root Cause**: The `_convert_behave_step` method didn't track the previous step type, causing And/But/* steps to always default to 'given'.

**Fix**: Updated parser to track previous step type throughout each scenario and pass it to step converter. And/But/* steps now correctly inherit:
- And/But/* after Given → `@given`
- And/But/* after When → `@when`
- And/But/* after Then → `@then`

**Impact**: This aligns with the Gherkin specification which states that And/But/* are syntactic sugar that inherit the step type from context.

**Testing**: Added comprehensive test `test_and_but_step_inheritance` covering all inheritance scenarios.

**Files Changed**:
- `generate_stubs.py`: Updated `_extract_steps_from_feature` and `_convert_behave_step`
- `test_generate_stubs.py`: Added new test case
- Test suite: 30 tests, all passing

---

## [1.2.0] - 2026-01-08

### 📚 Documentation Overhaul

#### Progressive Disclosure Architecture
- **Before**: 530-line SKILL.md with all content in one file
- **After**: Split into focused files following Agent Skills specification best practices
  - `SKILL.md` (285 lines) - Core instructions only
  - `references/EXAMPLES.md` - Extended usage examples
  - `references/TROUBLESHOOTING.md` - Error handling and common issues
  - `references/ADVANCED_USAGE.md` - Integration patterns and workflows
- **Impact**: Faster context loading, easier navigation, better progressive disclosure

#### New Documentation Files

**EXAMPLES.md** - Comprehensive examples including:
- Basic single-file and multi-file usage
- Parameter handling (strings, numbers, semantic types, scenario outlines)
- Data tables and doc strings
- Complete BDD workflow integration (user login feature end-to-end)
- Advanced usage patterns

**TROUBLESHOOTING.md** - Complete troubleshooting guide:
- Common errors (file not found, invalid extension, file exists)
- File and path issues
- Parsing issues (wrong parameter names, function conflicts)
- Generation issues (import errors, syntax errors)
- Type inference issues
- Integration issues (Behave can't find steps, similarity detection)
- FAQ with workarounds

**ADVANCED_USAGE.md** - Integration and automation:
- BDD Red-Green-Refactor cycle integration
- CI/CD examples (GitHub Actions, GitLab CI, Jenkins)
- Pre-commit hooks (with and without framework)
- Programmatic usage (import as module)
- Multi-project strategies
- Performance optimization (parallel processing, caching)
- Custom workflows (auto-regenerate, Makefile integration)

#### Improved SKILL.md
- Condensed from 530 to 285 lines
- Removed redundant content
- Added clear references to other documentation
- Better organization with focused sections
- Quick workflow section for common use cases

### 🔗 Cross-Reference Improvements
- All files now properly link to each other
- Clear navigation path for users
- "See X for Y" guidance throughout

### 📝 Agent Skills Spec Compliance
- SKILL.md under recommended 500-line limit (now 285 lines)
- Progressive disclosure with references/ directory
- Clear separation of core instructions vs. detailed examples
- Better metadata in frontmatter (version bumped to 1.2.0)

### Example Documentation Structure

**Before v1.2.0:**
```
SKILL.md (530 lines) - Everything in one file
README.md
CHANGELOG.md
IMPROVEMENTS.md
```

**After v1.2.0:**
```
SKILL.md (285 lines) - Core instructions only
README.md - Quick start
CHANGELOG.md - Version history
references/
  ├── EXAMPLES.md - Extended examples
  ├── TROUBLESHOOTING.md - Error handling
  ├── ADVANCED_USAGE.md - Integration patterns
  └── IMPROVEMENTS.md - Future enhancements
```

### Breaking Changes
None! This is purely a documentation reorganization. All functionality remains identical to v1.1.0.

---

## [1.1.0] - 2026-01-08

### 🚀 Major Improvements

#### Behave Parser Integration
- **Before**: Used fragile regex-based line-by-line parsing
- **After**: Uses Behave's official `parse_file()` for robust Gherkin parsing
- **Impact**: Now correctly handles Background, Scenario Outline, data tables, doc strings, and complex Gherkin constructs

#### Intelligent Type Inference
- **Before**: All parameters typed as `Any`
- **After**: Automatically infers `int`, `float`, `str`, `bool` from:
  - Pattern context (`{param:d}` → `int`, `{param:f}` → `float`)
  - Semantic meaning (age/count → `int`, price/rate → `float`, enabled/valid → `bool`)
- **Impact**: Generated code passes mypy strict checks without manual editing

#### Existing Step Detection
- **Before**: No awareness of existing step definitions
- **After**: AST-based scanner finds existing steps, calculates similarity, suggests reuse
- **Impact**: Prevents duplication, encourages step reuse, improves test maintainability

#### Data Table & Doc String Support
- **Before**: Silently ignored, no indication in generated code
- **After**: Detects and documents in step docstrings
  - "This step expects a data table in context.table"
  - "This step expects a doc string (json) in context.text"
- **Impact**: Developers know which steps need special handling

#### Proper Context Type
- **Before**: `context: Any`
- **After**: `from behave.runner import Context` + `context: Context`
- **Impact**: Better IDE autocomplete, type checking, code quality

#### Function Name Conflict Resolution
- **Before**: Could generate duplicate function names causing syntax errors
- **After**: Tracks used names, adds numeric suffix (`_2`, `_3`) for conflicts
- **Impact**: Generated code always compiles successfully

### ✨ New Features

#### CLI: `--check-existing` Flag
```bash
python generate_stubs.py features/new.feature --check-existing features/steps/
```
Scans existing step definition files and suggests similar steps for reuse.

### 🧪 Testing
- Added comprehensive test suite: 29 unit tests
- Coverage includes:
  - Type inference (7 tests)
  - Gherkin parsing (8 tests)
  - Existing step scanning (4 tests)
  - Stub generation (9 tests)
  - End-to-end integration (1 test)

### 📝 Documentation
- Updated SKILL.md with "What's New" section
- Updated README.md with new features
- Added IMPROVEMENTS.md with detailed implementation notes
- Updated examples to show new output format
- Documented all new CLI options

### 🔧 Code Quality
- Full type hints throughout
- Dataclasses for clean data structures
- AST parsing for robust Python code analysis
- Difflib for intelligent similarity matching
- Graceful fallback when Behave not installed

### Example Output Comparison

#### v1.0.0 Output
```python
from behave import given, when, then
from typing import Any

@given('a user with age {age:d}')
def step_a_user_with_age(context: Any, age: Any) -> None:
    raise NotImplementedError("Step not yet implemented")
```

#### v1.1.0 Output
```python
from behave import given, when, then
from behave.runner import Context

@given('a user with age {age:d}')
def a_user_with_age(context: Context, age: int) -> None:
    """TODO: Implement step: a user with age 30
"""
    raise NotImplementedError("Step not yet implemented")
```

**Improvements:**
- ✅ `Context` instead of `Any`
- ✅ `age: int` instead of `age: Any`
- ✅ Cleaner function name
- ✅ Better docstring

### Breaking Changes
None! The CLI interface is backward compatible. The only difference is improved output quality.

### Deprecations
None.

---

## [1.0.0] - 2026-01-08

### Initial Release
- Regex-based Gherkin parsing
- Parameter extraction for strings and numbers
- Behave decorator generation
- Multi-file support
- Step deduplication
- Organized output by step type (Given/When/Then)
