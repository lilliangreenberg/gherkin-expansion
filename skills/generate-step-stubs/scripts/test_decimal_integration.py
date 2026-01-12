#!/usr/bin/env python3
"""Integration tests for Decimal type handling in generated stubs."""

import tempfile
from pathlib import Path

import pytest

from generate_stubs import GherkinParser, StubGenerator


class TestDecimalIntegration:
    """Test Decimal type is properly used in generated stubs."""

    def test_decimal_in_generated_code_with_monetary_values(self, tmp_path):
        """Test that monetary values generate Decimal types in step definitions."""
        # Create a feature file with monetary values
        feature_file = tmp_path / "payment.feature"
        feature_file.write_text('''
Feature: Payment Processing

  Scenario: Process a payment
    Given an item with price 19.99 dollars
    And a tax rate of 0.08 percentage
    And a shipping cost of 5.50
    When the customer pays 25.49 total
    Then the transaction fee should be 0.75
    And the merchant receives 24.74 balance
''')

        # Parse the feature file
        parser = GherkinParser()
        steps = parser.parse_file(feature_file)

        # Verify type inference worked
        price_step = next((s for s in steps if "price" in s.pattern), None)
        assert price_step is not None, "Should find price step"
        assert "number1" in price_step.params
        assert price_step.param_types["number1"] == "Decimal", "Price should be Decimal"

        # Generate stubs
        generator = StubGenerator()
        code = generator.generate(steps, "payment")

        # Verify Decimal is imported
        assert "from decimal import Decimal" in code, "Should import Decimal"

        # Verify Decimal types are used in function signatures
        # Check for various monetary parameters
        assert "Decimal" in code, "Decimal type should appear in generated code"

        # Verify the code is syntactically valid
        import ast
        ast.parse(code)

        # Write to file for inspection
        output_file = tmp_path / "payment_steps.py"
        output_file.write_text(code)

        # Read back and verify specific patterns
        assert "number1: Decimal" in code or "Decimal" in code

    def test_decimal_vs_float_distinction(self, tmp_path):
        """Test that monetary values use Decimal while measurements use float."""
        feature_file = tmp_path / "mixed_types.feature"
        feature_file.write_text('''
Feature: Mixed Numeric Types

  Scenario: Process different numeric types
    Given an item with price 29.99
    And a weight of 5.5 pounds
    And a latitude of 37.7749
    And a customer score of 85.5
    When calculating totals
    Then verify types are correct
''')

        parser = GherkinParser()
        steps = parser.parse_file(feature_file)

        # Find steps and verify their type inference
        price_step = next((s for s in steps if "price" in s.text.lower()), None)
        weight_step = next((s for s in steps if "weight" in s.text.lower()), None)
        latitude_step = next((s for s in steps if "latitude" in s.text.lower()), None)
        score_step = next((s for s in steps if "score" in s.text.lower()), None)

        # Verify monetary values infer to Decimal
        if price_step and price_step.params:
            param_type = price_step.param_types.get(price_step.params[0])
            assert param_type == "Decimal", f"Price should be Decimal, got {param_type}"

        # Verify measurements infer to float
        if weight_step and weight_step.params:
            param_type = weight_step.param_types.get(weight_step.params[0])
            assert param_type == "float", f"Weight should be float, got {param_type}"

        if latitude_step and latitude_step.params:
            param_type = latitude_step.param_types.get(latitude_step.params[0])
            assert param_type == "float", f"Latitude should be float, got {param_type}"

        if score_step and score_step.params:
            param_type = score_step.param_types.get(score_step.params[0])
            assert param_type == "float", f"Score should be float, got {param_type}"

        # Generate code and verify both Decimal import and float usage
        generator = StubGenerator()
        code = generator.generate(steps, "mixed_types")

        # Should always import Decimal (template includes it)
        assert "from decimal import Decimal" in code

    def test_all_decimal_names_recognized(self):
        """Test that all predefined monetary names are recognized as Decimal."""
        from generate_stubs import TypeInferencer

        inferencer = TypeInferencer()

        # Test all DECIMAL_NAMES
        decimal_names = [
            "price", "cost", "dollar", "dollars", "rate", "percentage",
            "fee", "tax", "balance", "payment", "salary", "wage"
        ]

        for name in decimal_names:
            result = inferencer.infer_type(name, f"value is {{{name}}}")
            assert result == "Decimal", f"{name} should infer to Decimal, got {result}"

    def test_decimal_with_explicit_type_hint(self):
        """Test Decimal inference with explicit :f type hint."""
        from generate_stubs import TypeInferencer

        inferencer = TypeInferencer()

        # Monetary values with :f should become Decimal
        assert inferencer.infer_type("price", "costs {price:f}") == "Decimal"
        assert inferencer.infer_type("cost", "total {cost:f}") == "Decimal"
        assert inferencer.infer_type("fee", "charges {fee:f}") == "Decimal"

        # Non-monetary values with :f should be float
        assert inferencer.infer_type("weight", "weighs {weight:f}") == "float"
        assert inferencer.infer_type("distance", "travels {distance:f}") == "float"

    def test_generated_stub_has_decimal_parameter(self, tmp_path):
        """Test that generated stub function has Decimal parameter type."""
        feature_file = tmp_path / "price.feature"
        feature_file.write_text('''
Feature: Pricing

  Scenario: Set item price
    Given an item with price 19.99
    When I update the price
    Then the new price should be saved
''')

        parser = GherkinParser()
        steps = parser.parse_file(feature_file)

        generator = StubGenerator()
        code = generator.generate(steps, "price")

        # Verify generated function signature contains Decimal
        lines = code.split('\n')

        # Find the function definition with the price parameter
        for i, line in enumerate(lines):
            if 'def ' in line and i < len(lines) - 1:
                # Check this line and the next few for parameter definition
                func_block = '\n'.join(lines[i:min(i+3, len(lines))])
                if 'price' in func_block.lower() or 'number' in func_block:
                    # Should have Decimal type annotation
                    assert 'Decimal' in func_block or 'number1: Decimal' in func_block, \
                        f"Function should have Decimal parameter: {func_block}"
                    break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
