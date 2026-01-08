#!/usr/bin/env python3
"""Unit tests for generate_stubs.py."""

import tempfile
from pathlib import Path

import pytest

from generate_stubs import (
    ExistingStepDef,
    ExistingStepScanner,
    GherkinParser,
    Step,
    StubGenerator,
    TypeInferencer,
)


class TestTypeInferencer:
    """Tests for TypeInferencer."""

    def test_infer_type_from_pattern_int(self):
        """Test type inference from pattern - integer."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("count", "a database with {count:d} records") == "int"

    def test_infer_type_from_pattern_float(self):
        """Test type inference from pattern - float."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("price", "item costs {price:f}") == "float"

    def test_infer_type_from_pattern_quoted(self):
        """Test type inference from pattern - quoted string."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("name", 'a user named "{name}"') == "str"

    def test_infer_type_from_semantic_int(self):
        """Test type inference from semantic meaning - integer."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("age", "user has age") == "int"
        assert inferencer.infer_type("count", "database has count") == "int"
        assert inferencer.infer_type("port", "server on port") == "int"

    def test_infer_type_from_semantic_float(self):
        """Test type inference from semantic meaning - float."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("price", "item has price") == "float"
        assert inferencer.infer_type("latitude", "location at latitude") == "float"
        assert inferencer.infer_type("percentage", "success percentage") == "float"

    def test_infer_type_from_semantic_bool(self):
        """Test type inference from semantic meaning - boolean."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("enabled", "feature enabled") == "bool"
        assert inferencer.infer_type("valid", "data valid") == "bool"

    def test_infer_type_default_str(self):
        """Test default type inference - string."""
        inferencer = TypeInferencer()
        assert inferencer.infer_type("username", "user username") == "str"
        assert inferencer.infer_type("unknown", "some unknown") == "str"


class TestGherkinParser:
    """Tests for GherkinParser."""

    def test_extract_parameters_quoted_string(self):
        """Test parameter extraction - quoted strings."""
        parser = GherkinParser()
        pattern, params = parser._extract_parameters('a file named "test.txt"')

        assert pattern == 'a file named "{test_txt}"'
        assert params == ["test_txt"]

    def test_extract_parameters_number(self):
        """Test parameter extraction - numbers."""
        parser = GherkinParser()
        pattern, params = parser._extract_parameters("a database with 10 records")

        assert pattern == "a database with {number1:d} records"
        assert params == ["number1"]

    def test_extract_parameters_float(self):
        """Test parameter extraction - floating point."""
        parser = GherkinParser()
        pattern, params = parser._extract_parameters("item costs 9.99 dollars")

        assert pattern == "item costs {number1:f} dollars"
        assert params == ["number1"]

    def test_extract_parameters_multiple(self):
        """Test parameter extraction - multiple parameters."""
        parser = GherkinParser()
        pattern, params = parser._extract_parameters(
            'a user "alice" with age 30 and email "alice@test.com"'
        )

        assert len(params) == 3
        assert 'alice' in pattern
        assert '{number1:d}' in pattern
        assert 'alice_test_com' in pattern

    def test_extract_parameters_scenario_outline(self):
        """Test parameter extraction - scenario outline parameters."""
        parser = GherkinParser()
        pattern, params = parser._extract_parameters("a value of <amount>")

        assert pattern == "a value of {amount}"
        assert params == ["amount"]

    def test_deduplicate_steps(self):
        """Test step deduplication."""
        parser = GherkinParser()
        steps = [
            Step("given", "a user", "a user", [], {}),
            Step("given", "a user", "a user", [], {}),  # Duplicate
            Step("when", "I login", "I login", [], {}),
        ]
        parser.steps = steps
        unique = parser._deduplicate_steps(steps)

        assert len(unique) == 2
        assert unique[0].step_type == "given"
        assert unique[1].step_type == "when"

    def test_parse_content_fallback(self):
        """Test fallback parsing (without behave)."""
        parser = GherkinParser()
        content = """
        Feature: Login

          Scenario: Successful login
            Given a user with username "alice"
            When the user logs in
            Then the user should see welcome message
        """
        steps = parser._parse_content_fallback(content)

        assert len(steps) == 3
        assert steps[0].step_type == "given"
        assert steps[0].pattern == 'a user with username "{alice}"'
        assert steps[1].step_type == "when"
        assert steps[2].step_type == "then"

    def test_is_numeric(self):
        """Test numeric detection."""
        parser = GherkinParser()

        assert parser._is_numeric("123")
        assert parser._is_numeric("123.45")
        assert parser._is_numeric("0.5")
        assert not parser._is_numeric("abc")
        assert not parser._is_numeric("12abc")

    def test_and_but_step_inheritance(self, tmp_path):
        """Test that And/But/* steps inherit step type from previous step."""
        parser = GherkinParser()

        # Create test feature with And/But steps
        feature_file = tmp_path / "test.feature"
        feature_file.write_text("""
Feature: Test And/But Inheritance

  Scenario: Test proper inheritance
    Given a user exists
    And the user is authenticated
    When the user logs in
    And the user navigates to dashboard
    But the user has no notifications
    Then the user should see welcome message
    And the dashboard should be displayed
    But the notifications panel should be empty
""")

        steps = parser.parse_file(feature_file)

        # Verify step types
        assert len(steps) == 8

        # Given and And after Given
        assert steps[0].step_type == "given"
        assert steps[0].text == "a user exists"
        assert steps[1].step_type == "given"  # And inherits from Given
        assert steps[1].text == "the user is authenticated"

        # When and And/But after When
        assert steps[2].step_type == "when"
        assert steps[2].text == "the user logs in"
        assert steps[3].step_type == "when"  # And inherits from When
        assert steps[3].text == "the user navigates to dashboard"
        assert steps[4].step_type == "when"  # But inherits from When
        assert steps[4].text == "the user has no notifications"

        # Then and And/But after Then
        assert steps[5].step_type == "then"
        assert steps[5].text == "the user should see welcome message"
        assert steps[6].step_type == "then"  # And inherits from Then
        assert steps[6].text == "the dashboard should be displayed"
        assert steps[7].step_type == "then"  # But inherits from Then
        assert steps[7].text == "the notifications panel should be empty"


class TestExistingStepScanner:
    """Tests for ExistingStepScanner."""

    def test_parse_file_with_steps(self, tmp_path):
        """Test parsing a file with step definitions."""
        scanner = ExistingStepScanner()

        # Create a test step file
        step_file = tmp_path / "test_steps.py"
        step_file.write_text('''
from behave import given, when, then

@given('a user named "{name}"')
def step_user_named(context, name):
    pass

@when('the user logs in')
def step_user_login(context):
    pass

@then('the user should see "{message}"')
def step_user_see(context, message):
    pass
''')

        steps = scanner._parse_file(step_file)

        assert len(steps) == 3
        assert steps[0].step_type == "given"
        assert steps[0].pattern == 'a user named "{name}"'
        assert steps[0].function_name == "step_user_named"
        assert steps[0].line_number == 5  # Line number in generated file
        assert steps[1].step_type == "when"
        assert steps[2].step_type == "then"

    def test_scan_directory(self, tmp_path):
        """Test scanning a directory for step definitions."""
        scanner = ExistingStepScanner()

        # Create test step files
        (tmp_path / "auth_steps.py").write_text('''
from behave import given

@given('a user exists')
def step_user_exists(context):
    pass
''')

        (tmp_path / "api_steps.py").write_text('''
from behave import when

@when('I call the API')
def step_call_api(context):
    pass
''')

        steps = scanner.scan_directory(tmp_path)

        assert len(steps) == 2
        assert any(s.pattern == "a user exists" for s in steps)
        assert any(s.pattern == "I call the API" for s in steps)

    def test_find_similar_steps(self):
        """Test finding similar steps."""
        scanner = ExistingStepScanner()

        new_step = Step(
            step_type="given",
            text='a user with name "alice"',
            pattern='a user with name "{name}"',
            params=["name"],
            param_types={"name": "str"},
        )

        existing_steps = [
            ExistingStepDef(
                step_type="given",
                pattern='a user named "{username}"',
                function_name="step_user_named",
                file_path=Path("auth_steps.py"),
                line_number=10,
            ),
            ExistingStepDef(
                step_type="when",
                pattern="the user logs in",
                function_name="step_user_login",
                file_path=Path("auth_steps.py"),
                line_number=15,
            ),
        ]

        similar = scanner.find_similar_steps(new_step, existing_steps, threshold=0.5)

        assert len(similar) == 1
        similarity, step = similar[0]
        assert similarity > 0.5
        assert step.pattern == 'a user named "{username}"'

    def test_find_similar_steps_no_match(self):
        """Test finding similar steps with no matches."""
        scanner = ExistingStepScanner()

        new_step = Step(
            step_type="given",
            text="a completely different step",
            pattern="a completely different step",
            params=[],
            param_types={},
        )

        existing_steps = [
            ExistingStepDef(
                step_type="given",
                pattern='a user named "{username}"',
                function_name="step_user_named",
                file_path=Path("auth_steps.py"),
                line_number=10,
            ),
        ]

        similar = scanner.find_similar_steps(new_step, existing_steps, threshold=0.8)

        assert len(similar) == 0


class TestStubGenerator:
    """Tests for StubGenerator."""

    def test_generate_function_name_base(self):
        """Test function name generation."""
        generator = StubGenerator()

        step = Step(
            step_type="given",
            text='a file named "test.txt"',
            pattern='a file named "{filename}"',
            params=["filename"],
            param_types={"filename": "str"},
        )

        name = generator._generate_function_name_base(step)

        assert name == "a_file_named"
        assert name.isidentifier()  # Valid Python identifier

    def test_generate_function_name_long_truncation(self):
        """Test function name truncation for long steps."""
        generator = StubGenerator()

        step = Step(
            step_type="given",
            text="a very long step text that should be truncated because it exceeds the maximum length",
            pattern="a very long step text that should be truncated because it exceeds the maximum length",
            params=[],
            param_types={},
        )

        name = generator._generate_function_name_base(step)

        assert len(name) <= 50
        assert name.isidentifier()

    def test_generate_unique_function_name(self):
        """Test unique function name generation with conflicts."""
        generator = StubGenerator()

        step1 = Step(
            step_type="given",
            text="a user exists",
            pattern="a user exists",
            params=[],
            param_types={},
        )
        step2 = Step(
            step_type="given",
            text="a user exists",  # Duplicate
            pattern="a user exists",
            params=[],
            param_types={},
        )

        name1 = generator._generate_unique_function_name(step1)
        name2 = generator._generate_unique_function_name(step2)

        assert name1 == "a_user_exists"
        assert name2 == "a_user_exists_2"
        assert name1 != name2

    def test_generate_basic_stub(self):
        """Test generating a basic stub."""
        generator = StubGenerator()

        steps = [
            Step(
                step_type="given",
                text='a user named "alice"',
                pattern='a user named "{name}"',
                params=["name"],
                param_types={"name": "str"},
            )
        ]

        code = generator.generate(steps, "test")

        assert "from behave import given, when, then" in code
        assert "from behave.runner import Context" in code
        assert '@given(\'a user named "{name}"\')' in code
        assert "def " in code
        assert "context: Context" in code
        assert "name: str" in code
        assert "raise NotImplementedError" in code

    def test_generate_stub_with_data_table(self):
        """Test generating stub with data table."""
        generator = StubGenerator()

        steps = [
            Step(
                step_type="given",
                text="the following users",
                pattern="the following users",
                params=[],
                param_types={},
                has_table=True,
            )
        ]

        code = generator.generate(steps, "test")

        assert "data table in context.table" in code

    def test_generate_stub_with_docstring(self):
        """Test generating stub with doc string."""
        generator = StubGenerator()

        steps = [
            Step(
                step_type="given",
                text="a file with content",
                pattern="a file with content",
                params=[],
                param_types={},
                has_docstring=True,
                docstring_content_type="json",
            )
        ]

        code = generator.generate(steps, "test")

        assert "doc string (json) in context.text" in code

    def test_generate_stub_with_similar_existing(self):
        """Test generating stub with similar existing step."""
        existing_steps = [
            ExistingStepDef(
                step_type="given",
                pattern='a user with username "{username}"',
                function_name="step_user_with_username",
                file_path=Path("auth_steps.py"),
                line_number=42,
            )
        ]

        generator = StubGenerator(existing_steps=existing_steps)

        steps = [
            Step(
                step_type="given",
                text='a user with name "alice"',
                pattern='a user with name "{name}"',
                params=["name"],
                param_types={"name": "str"},
            )
        ]

        code = generator.generate(steps, "test")

        assert "Similar step exists" in code
        assert "auth_steps.py:42" in code
        assert "Consider reusing or refactoring" in code

    def test_generate_with_multiple_step_types(self):
        """Test generating stubs with all step types."""
        generator = StubGenerator()

        steps = [
            Step("given", "a user exists", "a user exists", [], {}),
            Step("when", "the user logs in", "the user logs in", [], {}),
            Step("then", "the user should be authenticated", "the user should be authenticated", [], {}),
        ]

        code = generator.generate(steps, "test")

        assert "# Given Steps - Setup and Preconditions" in code
        assert "# When Steps - Actions and Events" in code
        assert "# Then Steps - Assertions and Verification" in code
        assert '@given(' in code
        assert '@when(' in code
        assert '@then(' in code

    def test_generate_with_type_inference(self):
        """Test generating stubs with proper type inference."""
        generator = StubGenerator()

        steps = [
            Step(
                step_type="given",
                text="a database with 10 records",
                pattern="a database with {count:d} records",
                params=["count"],
                param_types={"count": "int"},
            ),
            Step(
                step_type="when",
                text='I upload file "test.pdf"',
                pattern='I upload file "{filename}"',
                params=["filename"],
                param_types={"filename": "str"},
            ),
        ]

        code = generator.generate(steps, "test")

        assert "count: int" in code
        assert "filename: str" in code


class TestIntegration:
    """Integration tests."""

    def test_end_to_end_parsing_and_generation(self, tmp_path):
        """Test complete workflow: parse feature file and generate stubs."""
        # Create a test feature file
        feature_file = tmp_path / "test.feature"
        feature_file.write_text('''
Feature: User Authentication

  Background:
    Given a clean database

  Scenario: Successful login
    Given a user with username "alice" and password "secret123"
    When the user submits the login form
    Then the user should be redirected to the dashboard
    And a welcome message should be displayed

  Scenario Outline: Failed login attempts
    Given a user with username "<username>"
    When the user enters password "<password>"
    Then the login should fail
    And an error message should be shown

    Examples:
      | username | password |
      | alice    | wrong    |
      | bob      | invalid  |
''')

        # Parse the feature file
        parser = GherkinParser()
        try:
            steps = parser.parse_file(feature_file)
        except ImportError:
            # If behave not installed, use fallback
            steps = parser._parse_file_fallback(feature_file)

        # Should have parsed all unique steps
        assert len(steps) > 0

        # Generate stubs
        generator = StubGenerator()
        code = generator.generate(steps, "test")

        # Verify output
        assert "from behave import given, when, then" in code
        assert "from behave.runner import Context" in code
        assert "def " in code  # Function definitions exist
        assert "raise NotImplementedError" in code

        # Write to file and verify it's valid Python
        output_file = tmp_path / "test_steps.py"
        output_file.write_text(code)

        # Verify it's syntactically valid Python
        import ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            pytest.fail(f"Generated code is not valid Python: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
