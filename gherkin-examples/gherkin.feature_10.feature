@passing
Feature: Configuration and Settings Management

  As a user
  I want to configure the tool's behavior
  So that I can customize it to my needs and save my preferences

  Rule: Configuration must follow XDG Base Directory specification

    Scenario: Use XDG_CONFIG_HOME for configuration files
      Given XDG_CONFIG_HOME is set to "/home/user/.config"
      When I load the configuration
      Then the config file should be loaded from "/home/user/.config/meeting-extractor/config.toml"

    Scenario: Fallback to default config location when XDG_CONFIG_HOME is not set
      Given XDG_CONFIG_HOME is not set
      When I load the configuration
      Then the config file should be loaded from "~/.config/meeting-extractor/config.toml"

    Scenario: Use XDG_DATA_HOME for output data
      Given XDG_DATA_HOME is set to "/home/user/.local/share"
      When I save extraction results with default output directory
      Then files should be saved to "/home/user/.local/share/meeting-extractor/minutes"

    Scenario: Use XDG_CACHE_HOME for cache files
      Given XDG_CACHE_HOME is set to "/home/user/.cache"
      When I need to cache data
      Then cache files should be stored in "/home/user/.cache/meeting-extractor"

  Rule: Configuration file must support all major settings

    Scenario: Load API configuration from file
      Given a config file with API settings:
        """
        [api]
        provider = "anthropic"
        model = "claude-sonnet-4-5-20251101"
        timeout = 60
        max_retries = 3
        """
      When I load the configuration
      Then the API provider should be "anthropic"
      And the model should be "claude-sonnet-4-5-20251101"
      And the timeout should be 60 seconds
      And max retries should be 3

    Scenario: Load extraction settings from file
      Given a config file with extraction settings:
        """
        [extraction]
        confidence_threshold = 0.7
        temperature = 0.0
        max_tokens = 4096
        """
      When I load the configuration
      Then the confidence threshold should be 0.7
      And the temperature should be 0.0
      And the max tokens should be 4096

    Scenario: Load urgency keywords from file
      Given a config file with urgency settings:
        """
        [urgency]
        high_keywords = ["urgent", "ASAP", "critical"]
        medium_keywords = ["soon", "important"]
        low_keywords = ["eventually", "nice to have"]
        """
      When I load the configuration
      Then high urgency keywords should include "urgent", "ASAP", "critical"
      And medium urgency keywords should include "soon", "important"
      And low urgency keywords should include "eventually", "nice to have"

    Scenario: Load output settings from file
      Given a config file with output settings:
        """
        [output]
        directory = "~/Documents/meeting-minutes"
        include_json = true
        include_confidence_scores = true
        template = "default"
        """
      When I load the configuration
      Then the output directory should be "~/Documents/meeting-minutes"
      And JSON output should be enabled
      And confidence scores should be included
      And the template should be "default"

  Rule: Default configuration must be sensible

    Scenario: Use default configuration when no config file exists
      Given no configuration file exists
      When I load the configuration
      Then default settings should be used
      And the API model should be "claude-sonnet-4-5-20251101"
      And the confidence threshold should be 0.7
      And the temperature should be 0.0
      And the output directory should be XDG-compliant default

  Rule: Environment variables must override configuration file

    Scenario: API key from environment variable
      Given the ANTHROPIC_API_KEY environment variable is set to "test-key"
      When I initialize the application
      Then the API key should be "test-key"

    Scenario: Model selection from environment variable
      Given the MEETING_EXTRACTOR_MODEL environment variable is set to "claude-opus-4"
      And the config file specifies model "claude-sonnet-4-5"
      When I load the configuration
      Then the model should be "claude-opus-4"
      And the environment variable should override the config file

  Rule: Configuration validation must prevent invalid settings

    Scenario: Validate confidence threshold range
      Given a config file with confidence_threshold = 1.5
      When I load the configuration
      Then validation should fail
      And an error message should explain "confidence_threshold must be between 0.0 and 1.0"

    Scenario: Validate temperature range
      Given a config file with temperature = 2.5
      When I load the configuration
      Then validation should fail
      And an error message should explain "temperature must be between 0.0 and 1.0"

    Scenario: Validate max file size
      Given a config file with max_file_size_mb = -1
      When I load the configuration
      Then validation should fail
      And an error message should explain "max_file_size_mb must be positive"

  Rule: Configuration creation and initialization

    Scenario: Generate default configuration file
      Given no configuration file exists
      When I run "meeting-extract --init-config"
      Then a default config file should be created at the XDG config location
      And the file should contain all configuration sections with defaults
      And a success message should confirm creation

    Scenario: Don't overwrite existing configuration
      Given a configuration file already exists
      When I run "meeting-extract --init-config"
      Then the existing file should not be overwritten
      And an error message should say "Configuration file already exists"

    Scenario: Force overwrite existing configuration
      Given a configuration file already exists
      When I run "meeting-extract --init-config --force"
      Then the existing file should be backed up
      And a new default config file should be created
      And a message should confirm the backup location

  Rule: Configuration must be documented

    Scenario: Generated config file includes documentation
      When I generate a default configuration file
      Then the file should include comments explaining each setting
      And each section should have a description
      And example values should be provided
      And links to documentation should be included

  Rule: Multiple configuration sources must be merged properly

    Scenario: Merge configuration from multiple sources
      Given a config file specifies some settings
      And environment variables specify other settings
      And command-line arguments specify additional settings
      When I load the configuration
      Then command-line arguments should have highest priority
      And environment variables should override config file
      And config file should provide defaults for unspecified settings
      And the merged configuration should be consistent and valid
