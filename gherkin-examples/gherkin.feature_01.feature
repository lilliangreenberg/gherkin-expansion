@passing
Feature: Project Foundation and Setup

  As a developer
  I want to set up a proper Python project structure
  So that I have a solid foundation for building the meeting extractor tool

  Rule: Project must follow src/ layout pattern

    Scenario: Initialize project structure with src/ layout
      Given I am in an empty project directory
      When I create the project structure
      Then the "src/meeting_extractor" directory should exist
      And the "src/meeting_extractor/core" directory should exist
      And the "src/meeting_extractor/infrastructure" directory should exist
      And the "tests" directory should exist
      And the "pyproject.toml" file should exist

    Scenario: Configure package management with uv
      Given I am in the project root directory
      When I initialize the project with uv
      Then the "pyproject.toml" should specify Python 3.12+ as minimum version
      And the "pyproject.toml" should include all required dependencies
      And I should be able to run "uv sync" successfully

  Rule: Development tools must be properly configured

    Scenario: Configure ruff for linting and formatting
      Given the project is initialized
      When I configure ruff in "pyproject.toml"
      Then ruff should be configured for linting
      And ruff should be configured for formatting
      And running "ruff check ." should complete without errors on valid code

    Scenario: Configure mypy for strict type checking
      Given the project is initialized
      When I configure mypy in "pyproject.toml"
      Then mypy should be configured in strict mode
      And the mypy configuration should enforce full type hints
      And running "mypy src/" should complete without errors on valid code

    Scenario: Configure pytest for testing
      Given the project is initialized
      When I configure pytest in "pyproject.toml"
      Then pytest should be configured with 95% coverage requirement
      And pytest should be configured to use the src/ layout
      And running "pytest" should discover and run tests

    Scenario: Configure structlog for logging
      Given the project is initialized
      When I add structlog to dependencies
      Then I should be able to import structlog in my code
      And structlog should be configured with sensible defaults

  Rule: Project must follow XDG Base Directory standards

    Scenario: Set up XDG-compliant directory structure
      Given the project is initialized
      When I implement XDG directory support
      Then configuration files should respect XDG_CONFIG_HOME
      And data files should respect XDG_DATA_HOME
      And cache files should respect XDG_CACHE_HOME
      And appropriate fallback directories should be used when XDG variables are not set

  Rule: Project must have proper .gitignore

    Scenario: Create comprehensive .gitignore
      Given I am in the project root directory
      When I create the .gitignore file
      Then it should ignore Python cache files (__pycache__, *.pyc)
      And it should ignore virtual environment directories
      And it should ignore IDE configuration files
      And it should ignore build artifacts (dist/, build/, *.egg-info)
      And it should ignore .env files
      And it should ignore test coverage reports
