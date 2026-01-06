@passing
Feature: CLI Interface

  As a user
  I want a clear and intuitive command-line interface
  So that I can easily extract meeting information with various options

  Rule: Basic CLI commands must be simple and intuitive

    Scenario: Process single file with basic command
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf"
      Then the file should be processed
      And results should be displayed for review
      And upon approval, results should be saved to default location

    Scenario: Process multiple files with basic command
      Given I have files "meeting1.pdf", "meeting2.md", "meeting3.txt"
      When I run "meeting-extract meeting1.pdf meeting2.md meeting3.txt"
      Then all files should be processed in batch mode
      And results should be saved to default location

    Scenario: Process files with glob pattern
      Given I have multiple PDF files in "meetings/" directory
      When I run "meeting-extract meetings/*.pdf"
      Then all matching PDF files should be processed

  Rule: Output options must be flexible

    Scenario: Specify custom output directory
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --output-dir /custom/path"
      Then results should be saved to "/custom/path"
      And the directory should be created if it doesn't exist

    Scenario: Specify custom output filename
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --output custom_name.md"
      Then results should be saved as "custom_name.md"

    Scenario: Export JSON alongside markdown
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --json"
      Then both markdown and JSON files should be created

  Rule: Processing flags must control behavior

    Scenario: Skip user review with --no-review flag
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --no-review"
      Then results should be saved automatically without prompting

    Scenario: Force processing of ambiguous content
      Given I have a file with ambiguous content "unclear_meeting.pdf"
      When I run "meeting-extract unclear_meeting.pdf --force"
      Then processing should proceed despite ambiguity warnings
      And low confidence items should be marked in output

    Scenario: Dry run mode to preview without saving
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --dry-run"
      Then extraction should be performed
      And results should be displayed
      But no files should be written to disk

  Rule: Verbosity levels must control output detail

    Scenario: Verbose mode shows detailed processing information
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --verbose"
      Then detailed logging should be displayed
      And API calls should be logged
      And processing steps should be shown
      And timing information should be included

    Scenario: Quiet mode shows minimal output
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --quiet"
      Then only essential output should be shown
      And progress indicators should be minimal
      And only errors and final results should be displayed

    Scenario: Debug mode for troubleshooting
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --debug"
      Then all debug information should be logged
      And API request/response details should be shown
      And internal processing steps should be visible

  Rule: Configuration file support must be available

    Scenario: Load configuration from default location
      Given a config file exists at XDG_CONFIG_HOME/meeting-extractor/config.toml
      When I run "meeting-extract meeting.pdf"
      Then configuration should be loaded from the default location
      And settings should be applied to the processing

    Scenario: Load configuration from custom file
      Given a config file at "/custom/config.toml"
      When I run "meeting-extract meeting.pdf --config /custom/config.toml"
      Then configuration should be loaded from "/custom/config.toml"
      And it should override default settings

    Scenario: Command-line arguments override configuration file
      Given a config file sets confidence_threshold to 0.7
      When I run "meeting-extract meeting.pdf --confidence-threshold 0.8"
      Then the confidence threshold should be 0.8
      And the command-line value should take precedence

  Rule: Help and version information must be accessible

    Scenario: Display help with --help flag
      When I run "meeting-extract --help"
      Then comprehensive help text should be displayed
      And all command options should be documented
      And usage examples should be shown

    Scenario: Display version with --version flag
      When I run "meeting-extract --version"
      Then the version number should be displayed
      And the program should exit

  Rule: Advanced options must be supported

    Scenario: Set custom confidence threshold
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --confidence-threshold 0.6"
      Then items with confidence >= 0.6 should be accepted
      And items with confidence < 0.6 should be flagged as low confidence

    Scenario: Select specific Claude model
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --model claude-opus-4"
      Then the extraction should use claude-opus-4 instead of the default model

    Scenario: Set custom API timeout
      Given I have a file "meeting.pdf"
      When I run "meeting-extract meeting.pdf --timeout 90"
      Then the API timeout should be set to 90 seconds

  Rule: Error messages must be clear and actionable

    Scenario: Show clear error for missing file
      When I run "meeting-extract nonexistent.pdf"
      Then an error message should be displayed
      And it should say "File not found: nonexistent.pdf"

    Scenario: Show clear error for missing API key
      Given ANTHROPIC_API_KEY is not set
      When I run "meeting-extract meeting.pdf"
      Then an error message should be displayed
      And it should say "ANTHROPIC_API_KEY environment variable not set"
      And it should provide instructions on how to set it

    Scenario: Show clear error for unsupported file type
      When I run "meeting-extract document.docx"
      Then an error message should be displayed
      And it should say "Unsupported file type: .docx"
      And it should list supported file types
