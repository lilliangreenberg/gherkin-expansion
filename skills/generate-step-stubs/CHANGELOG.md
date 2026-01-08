# Changelog

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
