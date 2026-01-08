#!/usr/bin/env python3
"""Generate Python step definition stubs from Gherkin feature files.

This script parses Gherkin feature files using Behave's parser and generates
Python step definition stubs with proper type hints and existing step detection.
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


@dataclass
class Step:
    """Represents a Gherkin step."""

    step_type: str  # 'given', 'when', 'then'
    text: str  # Original step text
    pattern: str  # Regex pattern for matching
    params: list[str]  # Parameter names
    param_types: dict[str, str] = field(default_factory=dict)  # Parameter types
    has_table: bool = False  # Has data table
    has_docstring: bool = False  # Has doc string
    docstring_content_type: str | None = None  # Doc string content type


@dataclass
class ExistingStepDef:
    """Represents an existing step definition."""

    step_type: str
    pattern: str
    function_name: str
    file_path: Path
    line_number: int


class TypeInferencer:
    """Infer parameter types from patterns and names."""

    INT_NAMES = {
        "count",
        "number",
        "num",
        "age",
        "size",
        "length",
        "quantity",
        "amount",
        "total",
        "index",
        "id",
        "port",
        "code",
        "status",
        "year",
        "month",
        "day",
    }

    FLOAT_NAMES = {
        "price",
        "cost",
        "rate",
        "percentage",
        "ratio",
        "latitude",
        "longitude",
        "score",
        "value",
        "weight",
        "height",
        "distance",
    }

    BOOL_NAMES = {
        "enabled",
        "disabled",
        "active",
        "inactive",
        "valid",
        "invalid",
        "required",
        "optional",
        "success",
        "failure",
        "exists",
    }

    def infer_type(self, param_name: str, pattern_context: str) -> str:
        """
        Infer Python type for a parameter.

        Args:
            param_name: Name of the parameter
            pattern_context: The pattern containing the parameter

        Returns:
            Python type annotation string
        """
        # Check pattern for explicit type hints
        if f"{{{param_name}:d}}" in pattern_context:
            return "int"
        elif f"{{{param_name}:f}}" in pattern_context:
            return "float"
        elif f"{{{param_name}:w}}" in pattern_context:
            return "str"  # Word
        elif f'"{{{param_name}}}"' in pattern_context:
            return "str"  # Quoted

        # Semantic inference from name
        clean_name = param_name.lower().strip("_")

        if clean_name in self.INT_NAMES:
            return "int"
        elif clean_name in self.FLOAT_NAMES:
            return "float"
        elif clean_name in self.BOOL_NAMES:
            return "bool"

        # Default to str
        return "str"


class ExistingStepScanner:
    """Scans for existing step definitions in Python files."""

    def scan_directory(self, steps_dir: Path) -> list[ExistingStepDef]:
        """
        Scan all Python files in steps directory.

        Args:
            steps_dir: Directory containing step definition files

        Returns:
            List of existing step definitions
        """
        if not steps_dir.exists() or not steps_dir.is_dir():
            return []

        existing_steps: list[ExistingStepDef] = []

        for py_file in steps_dir.glob("**/*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                existing_steps.extend(self._parse_file(py_file))
            except Exception:
                # Skip files that can't be parsed
                continue

        return existing_steps

    def _parse_file(self, file_path: Path) -> list[ExistingStepDef]:
        """
        Parse a Python file for step definitions using AST.

        Args:
            file_path: Path to Python file

        Returns:
            List of step definitions found in file
        """
        steps: list[ExistingStepDef] = []

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            return steps

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for @given/@when/@then decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, "id"):
                            decorator_name = decorator.func.id
                            if decorator_name in ("given", "when", "then"):
                                # Extract pattern from first argument
                                if decorator.args:
                                    pattern_node = decorator.args[0]
                                    if isinstance(pattern_node, ast.Constant):
                                        pattern = pattern_node.value
                                        steps.append(
                                            ExistingStepDef(
                                                step_type=decorator_name,
                                                pattern=pattern,
                                                function_name=node.name,
                                                file_path=file_path,
                                                line_number=node.lineno,
                                            )
                                        )

        return steps

    def find_similar_steps(
        self,
        new_step: Step,
        existing_steps: list[ExistingStepDef],
        threshold: float = 0.6,
    ) -> list[tuple[float, ExistingStepDef]]:
        """
        Find existing steps similar to new step.

        Args:
            new_step: New step to match
            existing_steps: List of existing step definitions
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of (similarity, step) tuples, sorted by similarity
        """
        similar: list[tuple[float, ExistingStepDef]] = []

        for existing in existing_steps:
            if existing.step_type != new_step.step_type:
                continue

            # Compare patterns
            similarity = SequenceMatcher(
                None, new_step.pattern.lower(), existing.pattern.lower()
            ).ratio()

            if similarity >= threshold:
                similar.append((similarity, existing))

        # Sort by similarity (highest first)
        similar.sort(reverse=True, key=lambda x: x[0])
        return similar


class GherkinParser:
    """Parses Gherkin feature files using Behave's parser."""

    PARAM_PATTERNS = [
        (r'"([^"]*)"', "string"),  # Quoted strings
        (r"'([^']*)'", "string"),  # Single quoted strings
        (r"<([^>]+)>", "param"),  # Scenario outline parameters
        (r"\{([^}]+)\}", "param"),  # Already parameterized steps
        (r"\b(\d+(?:\.\d+)?)\b", "number"),  # Numbers (int or float)
    ]

    def __init__(self) -> None:
        """Initialize parser."""
        self.type_inferencer = TypeInferencer()

    def parse_file(self, file_path: Path) -> list[Step]:
        """
        Parse a feature file using Behave's parser.

        Args:
            file_path: Path to the .feature file

        Returns:
            List of unique Step objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a .feature file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Feature file not found: {file_path}")

        if file_path.suffix != ".feature":
            raise ValueError(f"Expected .feature file, got: {file_path.suffix}")

        try:
            from behave.parser import parse_file as behave_parse_file

            feature = behave_parse_file(str(file_path))
        except ImportError:
            # Fallback to regex-based parsing if behave not available
            print(
                "Warning: behave not installed, using fallback parser",
                file=sys.stderr,
            )
            return self._parse_file_fallback(file_path)

        return self._extract_steps_from_feature(feature)

    def _extract_steps_from_feature(self, feature: Any) -> list[Step]:
        """
        Extract steps from Behave feature object.

        Args:
            feature: Behave Feature object

        Returns:
            List of Step objects
        """
        steps: list[Step] = []

        # Process Background steps
        if hasattr(feature, "background") and feature.background:
            previous_step_type: str | None = None
            for behave_step in feature.background.steps:
                step = self._convert_behave_step(behave_step, previous_step_type)
                steps.append(step)
                previous_step_type = step.step_type

        # Process Scenario steps
        if hasattr(feature, "scenarios"):
            for scenario in feature.scenarios:
                if hasattr(scenario, "steps"):
                    # Reset previous_step_type for each scenario
                    previous_step_type = None
                    for behave_step in scenario.steps:
                        step = self._convert_behave_step(behave_step, previous_step_type)
                        steps.append(step)
                        previous_step_type = step.step_type

        return self._deduplicate_steps(steps)

    def _convert_behave_step(
        self, behave_step: Any, previous_step_type: str | None = None
    ) -> Step:
        """
        Convert Behave step to our Step dataclass.

        Args:
            behave_step: Behave Step object
            previous_step_type: Step type from previous step (for And/But/* inheritance)

        Returns:
            Step object
        """
        # Normalize step type
        step_type = behave_step.keyword.lower().strip()
        if step_type in ("and", "but", "*"):
            # And/But/* inherit step type from previous step
            # If no previous step, default to 'given'
            step_type = previous_step_type if previous_step_type else "given"

        # Extract parameters and create pattern
        pattern, params = self._extract_parameters(behave_step.name)

        # Infer parameter types
        param_types = {
            param: self.type_inferencer.infer_type(param, pattern)
            for param in params
        }

        # Check for data table
        has_table = hasattr(behave_step, "table") and behave_step.table is not None

        # Check for doc string
        has_docstring = hasattr(behave_step, "text") and behave_step.text is not None
        docstring_content_type = None
        if has_docstring:
            docstring_content_type = getattr(
                behave_step.text, "content_type", None
            )

        return Step(
            step_type=step_type,
            text=behave_step.name,
            pattern=pattern,
            params=params,
            param_types=param_types,
            has_table=has_table,
            has_docstring=has_docstring,
            docstring_content_type=docstring_content_type,
        )

    def _parse_file_fallback(self, file_path: Path) -> list[Step]:
        """
        Fallback parser using regex (when Behave not available).

        Args:
            file_path: Path to feature file

        Returns:
            List of Step objects
        """
        content = file_path.read_text(encoding="utf-8")
        return self._parse_content_fallback(content)

    def _parse_content_fallback(self, content: str) -> list[Step]:
        """
        Parse Gherkin content using regex fallback.

        Args:
            content: Gherkin feature file content

        Returns:
            List of unique Step objects
        """
        steps: list[Step] = []
        current_step_type: str | None = None

        step_keywords = ("Given", "When", "Then", "And", "But", "*")

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines, comments, and non-step lines
            if not line or line.startswith("#"):
                continue

            # Check if line starts with a step keyword
            for keyword in step_keywords:
                if line.startswith(f"{keyword} "):
                    step_text = line[len(keyword) :].strip()

                    # Determine step type
                    if keyword == "Given":
                        current_step_type = "given"
                    elif keyword == "When":
                        current_step_type = "when"
                    elif keyword == "Then":
                        current_step_type = "then"
                    elif keyword in ("And", "But", "*"):
                        if not current_step_type:
                            current_step_type = "given"
                    else:
                        continue

                    # Extract parameters and create pattern
                    pattern, params = self._extract_parameters(step_text)

                    # Infer parameter types
                    param_types = {
                        param: self.type_inferencer.infer_type(param, pattern)
                        for param in params
                    }

                    step = Step(
                        step_type=current_step_type,
                        text=step_text,
                        pattern=pattern,
                        params=params,
                        param_types=param_types,
                    )

                    steps.append(step)
                    break

        return self._deduplicate_steps(steps)

    def _extract_parameters(self, text: str) -> tuple[str, list[str]]:
        """
        Extract parameters from step text and create regex pattern.

        Args:
            text: Step text

        Returns:
            Tuple of (regex_pattern, parameter_names)
        """
        pattern = text
        params: list[str] = []
        param_counter: dict[str, int] = {}

        # Collect all matches first with their positions
        all_matches: list[tuple[int, int, str, str, str]] = []

        for regex, param_type in self.PARAM_PATTERNS:
            for match in re.finditer(regex, text):
                # Store: (start_pos, end_pos, matched_text, full_match, param_type)
                all_matches.append(
                    (
                        match.start(),
                        match.end(),
                        match.group(1),
                        match.group(0),
                        param_type,
                    )
                )

        # Remove overlapping matches (keep first match)
        all_matches.sort(key=lambda x: x[0])
        filtered_matches: list[tuple[int, int, str, str, str]] = []
        last_end = -1

        for match in all_matches:
            start, end, matched_text, full_match, param_type = match
            if start >= last_end:
                filtered_matches.append(match)
                last_end = end

        # Process matches from right to left to preserve positions
        for start, end, matched_text, full_match, param_type in reversed(
            filtered_matches
        ):
            # Generate unique parameter name
            if param_type not in param_counter:
                param_counter[param_type] = 0

            param_counter[param_type] += 1

            # Use descriptive names when possible
            if matched_text and not self._is_numeric(matched_text):
                # Clean up parameter name
                param_name = re.sub(r"[^a-z0-9_]", "_", matched_text.lower())
                param_name = re.sub(r"_+", "_", param_name).strip("_")
                if not param_name or param_name[0].isdigit():
                    param_name = f"{param_type}{param_counter[param_type]}"
            else:
                param_name = f"{param_type}{param_counter[param_type]}"

            params.insert(0, param_name)  # Insert at beginning to maintain order

            # Create replacement pattern
            if param_type == "number":
                # Determine if int or float
                if "." in matched_text:
                    replacement = f"{{{param_name}:f}}"
                else:
                    replacement = f"{{{param_name}:d}}"
            elif param_type == "param":
                # Already has <> or {}, just use param name
                replacement = f"{{{param_name}}}"
            else:
                # Quoted string - keep quotes in pattern
                replacement = f'"{{{param_name}}}"'

            # Replace in pattern using position
            pattern = pattern[:start] + replacement + pattern[end:]

        return pattern, params

    def _is_numeric(self, text: str) -> bool:
        """Check if text is numeric."""
        try:
            float(text)
            return True
        except ValueError:
            return False

    def _deduplicate_steps(self, steps: list[Step]) -> list[Step]:
        """
        Remove duplicate steps based on pattern.

        Args:
            steps: List of steps

        Returns:
            List of unique steps
        """
        seen: set[tuple[str, str]] = set()
        unique_steps: list[Step] = []

        for step in steps:
            key = (step.step_type, step.pattern)
            if key not in seen:
                seen.add(key)
                unique_steps.append(step)

        return unique_steps


class StubGenerator:
    """Generates Python step definition stubs from steps."""

    TEMPLATE = '''"""Step definitions for {feature_name}."""
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# Given Steps - Setup and Preconditions
# ============================================================================

{given_steps}

# ============================================================================
# When Steps - Actions and Events
# ============================================================================

{when_steps}

# ============================================================================
# Then Steps - Assertions and Verification
# ============================================================================

{then_steps}
'''

    STEP_TEMPLATE = '''
@{decorator}('{pattern}')
def {function_name}(context: Context{params}) -> None:
    """TODO: Implement step: {original_text}
{extra_docs}"""
    raise NotImplementedError("Step not yet implemented")
'''

    STEP_WITH_SIMILAR_TEMPLATE = '''
@{decorator}('{pattern}')
def {function_name}(context: Context{params}) -> None:
    """TODO: Implement step: {original_text}

    NOTE: Similar step exists in {similar_file}:{similar_line}
    Pattern: {similar_pattern}
    Consider reusing or refactoring.
{extra_docs}"""
    raise NotImplementedError("Step not yet implemented")
'''

    def __init__(
        self, existing_steps: list[ExistingStepDef] | None = None
    ) -> None:
        """
        Initialize generator.

        Args:
            existing_steps: List of existing step definitions for reuse detection
        """
        self.existing_steps = existing_steps or []
        self.step_scanner = ExistingStepScanner()
        self.used_function_names: set[str] = set()

    def generate(
        self, steps: list[Step], feature_name: str = "feature"
    ) -> str:
        """
        Generate Python step definition stubs.

        Args:
            steps: List of Step objects
            feature_name: Name of the feature (for documentation)

        Returns:
            Python code with step definition stubs
        """
        # Reset function names for this generation
        self.used_function_names = set()

        # Group steps by type
        given_steps_list: list[Step] = []
        when_steps_list: list[Step] = []
        then_steps_list: list[Step] = []

        for step in steps:
            if step.step_type == "given":
                given_steps_list.append(step)
            elif step.step_type == "when":
                when_steps_list.append(step)
            elif step.step_type == "then":
                then_steps_list.append(step)

        # Generate stubs for each group
        given_stubs = self._generate_stubs(given_steps_list)
        when_stubs = self._generate_stubs(when_steps_list)
        then_stubs = self._generate_stubs(then_steps_list)

        # Fill template
        code = self.TEMPLATE.format(
            feature_name=feature_name,
            given_steps=given_stubs or "# No Given steps found",
            when_steps=when_stubs or "# No When steps found",
            then_steps=then_stubs or "# No Then steps found",
        )

        return code

    def _generate_stubs(self, steps: list[Step]) -> str:
        """
        Generate stubs for a list of steps.

        Args:
            steps: List of steps of the same type

        Returns:
            Python code with step definitions
        """
        if not steps:
            return ""

        stubs: list[str] = []

        for step in steps:
            # Generate unique function name
            function_name = self._generate_unique_function_name(step)

            # Generate parameter list with types
            params_str = ""
            if step.params:
                params_str = ", " + ", ".join(
                    f"{param}: {step.param_types.get(param, 'str')}"
                    for param in step.params
                )

            # Build extra documentation
            extra_docs_parts: list[str] = []
            if step.has_table:
                extra_docs_parts.append(
                    "    This step expects a data table in context.table"
                )
            if step.has_docstring:
                content_type = (
                    f" ({step.docstring_content_type})"
                    if step.docstring_content_type
                    else ""
                )
                extra_docs_parts.append(
                    f"    This step expects a doc string{content_type} in context.text"
                )

            extra_docs = (
                "\n" + "\n".join(extra_docs_parts) if extra_docs_parts else ""
            )

            # Check for similar existing steps
            similar_steps = self.step_scanner.find_similar_steps(
                step, self.existing_steps, threshold=0.6
            )

            if similar_steps:
                # Use template with similarity warning
                similarity, similar_step = similar_steps[0]
                stub = self.STEP_WITH_SIMILAR_TEMPLATE.format(
                    decorator=step.step_type,
                    pattern=step.pattern,
                    function_name=function_name,
                    params=params_str,
                    original_text=step.text,
                    similar_file=similar_step.file_path.name,
                    similar_line=similar_step.line_number,
                    similar_pattern=similar_step.pattern,
                    extra_docs=extra_docs,
                )
            else:
                # Use regular template
                stub = self.STEP_TEMPLATE.format(
                    decorator=step.step_type,
                    pattern=step.pattern,
                    function_name=function_name,
                    params=params_str,
                    original_text=step.text,
                    extra_docs=extra_docs,
                )

            stubs.append(stub.rstrip())

        return "\n".join(stubs)

    def _generate_unique_function_name(self, step: Step) -> str:
        """
        Generate a unique valid Python function name from step pattern.

        Args:
            step: Step object

        Returns:
            Unique valid Python function name
        """
        base_name = self._generate_function_name_base(step)

        # Ensure uniqueness
        if base_name not in self.used_function_names:
            self.used_function_names.add(base_name)
            return base_name

        # Add numeric suffix for conflicts
        counter = 2
        while f"{base_name}_{counter}" in self.used_function_names:
            counter += 1

        unique_name = f"{base_name}_{counter}"
        self.used_function_names.add(unique_name)
        return unique_name

    def _generate_function_name_base(self, step: Step) -> str:
        """
        Generate base function name from step pattern.

        Args:
            step: Step object

        Returns:
            Valid Python function name base
        """
        # Remove parameter placeholders
        text = re.sub(r"\{[^}]+\}", "", step.pattern)

        # Remove quotes
        text = text.replace('"', "").replace("'", "")

        # Convert to snake_case
        text = re.sub(r"[^a-z0-9]+", "_", text.lower())
        text = re.sub(r"_+", "_", text).strip("_")

        # Ensure it starts with a letter or underscore
        if text and text[0].isdigit():
            text = "step_" + text

        # Limit length to prevent overly long names
        if len(text) > 50:
            text = text[:50].rstrip("_")

        return text or "unnamed_step"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Python step definition stubs from Gherkin feature files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate stubs for a single feature file
  python generate_stubs.py features/login.feature

  # Generate stubs and save to file
  python generate_stubs.py features/login.feature -o features/steps/login_steps.py

  # Process multiple feature files
  python generate_stubs.py features/*.feature

  # Check for existing steps and suggest reuse
  python generate_stubs.py features/login.feature --check-existing features/steps/

  # Print to stdout
  python generate_stubs.py features/login.feature --stdout
        """,
    )

    parser.add_argument(
        "feature_files",
        nargs="+",
        type=Path,
        help="Path to one or more .feature files",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: feature_name_steps.py)",
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of file",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite output file if it exists",
    )

    parser.add_argument(
        "--check-existing",
        type=Path,
        metavar="STEPS_DIR",
        help="Directory containing existing step definitions (enables reuse detection)",
    )

    args = parser.parse_args()

    try:
        # Scan for existing steps if requested
        existing_steps: list[ExistingStepDef] = []
        if args.check_existing:
            scanner = ExistingStepScanner()
            existing_steps = scanner.scan_directory(args.check_existing)
            if existing_steps:
                print(
                    f"✓ Found {len(existing_steps)} existing step definitions in {args.check_existing}",
                    file=sys.stderr,
                )

        # Parse all feature files
        gherkin_parser = GherkinParser()
        all_steps: list[Step] = []
        feature_names: list[str] = []

        for feature_file in args.feature_files:
            try:
                steps = gherkin_parser.parse_file(feature_file)
                all_steps.extend(steps)
                feature_names.append(feature_file.stem)
                print(
                    f"✓ Parsed {len(steps)} unique steps from {feature_file}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"✗ Error parsing {feature_file}: {e}", file=sys.stderr)
                return 1

        if not all_steps:
            print("No steps found in feature files", file=sys.stderr)
            return 1

        # Deduplicate across all files
        seen: set[tuple[str, str]] = set()
        unique_steps: list[Step] = []
        for step in all_steps:
            key = (step.step_type, step.pattern)
            if key not in seen:
                seen.add(key)
                unique_steps.append(step)

        print(
            f"\n✓ Total {len(unique_steps)} unique steps across all files",
            file=sys.stderr,
        )

        # Generate stubs
        generator = StubGenerator(existing_steps=existing_steps)
        feature_name = "_".join(feature_names) if feature_names else "feature"
        code = generator.generate(unique_steps, feature_name)

        # Output
        if args.stdout:
            print(code)
        else:
            # Determine output path
            if args.output:
                output_path = args.output
            else:
                # Default: first_feature_name_steps.py
                output_path = Path(f"{feature_names[0]}_steps.py")

            # Check if file exists
            if output_path.exists() and not args.force:
                print(
                    f"✗ Output file {output_path} already exists. Use -f to overwrite.",
                    file=sys.stderr,
                )
                return 1

            # Write to file
            output_path.write_text(code, encoding="utf-8")
            print(
                f"\n✓ Generated step definitions: {output_path}",
                file=sys.stderr,
            )
            print(
                f"  Next steps:",
                file=sys.stderr,
            )
            print(
                f"  1. Review generated code and similarity warnings",
                file=sys.stderr,
            )
            print(
                f"  2. Update parameter types if needed (already inferred)",
                file=sys.stderr,
            )
            print(
                f"  3. Implement the step logic (replace NotImplementedError)",
                file=sys.stderr,
            )
            print(
                f"  4. Run: behave to test your implementation", file=sys.stderr
            )

        return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
