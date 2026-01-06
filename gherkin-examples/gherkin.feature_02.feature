@passing
Feature: Core Domain Models

  As a developer
  I want to define all core domain models with Pydantic
  So that I have type-safe, validated data structures for the application

  Rule: All models must use Pydantic with full type hints

    Scenario: Define MeetingMetadata model
      Given I am creating the core domain models
      When I define the MeetingMetadata model
      Then it should have a "title" field of type str
      And it should have a "date" field of type datetime
      And it should have a "participants" field of type list[str]
      And it should have a "duration" field of type timedelta or str
      And it should have a "source_file" field of type Path
      And it should have a "processed_at" field of type datetime
      And all fields should have proper Pydantic validation

    Scenario: Define Decision model
      Given I am creating the core domain models
      When I define the Decision model
      Then it should have a "content" field of type str for the decision made
      And it should have a "context" field of type str for surrounding context
      And it should have a "confidence" field of type float between 0.0 and 1.0
      And it should have a "source_section" field of type str
      And the confidence field should validate values are between 0.0 and 1.0

    Scenario: Define ActionItem model with urgency
      Given I am creating the core domain models
      When I define the ActionItem model
      Then it should have a "task" field of type str
      And it should have an "owner" field of type str or None
      And it should have a "deadline" field of type datetime or None
      And it should have an "urgency" field with literal values "High", "Medium", "Low"
      And it should have a "confidence" field of type float between 0.0 and 1.0
      And it should have a "dependencies" field of type list[str]
      And it should have a "status" field with literal value "extracted"
      And the confidence field should validate values are between 0.0 and 1.0

    Scenario: Define Risk model
      Given I am creating the core domain models
      When I define the Risk model
      Then it should have a "description" field of type str
      And it should have a "severity" field with literal values "High", "Medium", "Low" or None
      And it should have a "mitigation" field of type str or None
      And it should have a "confidence" field of type float between 0.0 and 1.0
      And it should have a "raised_by" field of type str or None
      And the confidence field should validate values are between 0.0 and 1.0

    Scenario: Define NextStep model
      Given I am creating the core domain models
      When I define the NextStep model
      Then it should have a "description" field of type str
      And it should have a "responsible_party" field of type str or None
      And it should have a "timeline" field of type str or None
      And it should have a "confidence" field of type float between 0.0 and 1.0
      And the confidence field should validate values are between 0.0 and 1.0

    Scenario: Define ExtractionResult aggregate model
      Given I have defined all component models
      When I define the ExtractionResult model
      Then it should have a "metadata" field of type MeetingMetadata
      And it should have a "decisions" field of type list[Decision]
      And it should have an "action_items" field of type list[ActionItem]
      And it should have a "risks" field of type list[Risk]
      And it should have a "next_steps" field of type list[NextStep]
      And it should have an "overall_confidence" field of type float
      And it should have an "ambiguity_warnings" field of type list[str]

    Scenario: Define ProcessingStatus model
      Given I am creating the core domain models
      When I define the ProcessingStatus model
      Then it should have a "file_path" field of type Path
      And it should have a "status" field with literal values "success", "failed", "skipped"
      And it should have an "error_message" field of type str or None
      And it should have an "output_path" field of type Path or None
      And it should have a "processing_time" field of type float

  Rule: All models must have comprehensive unit tests

    Scenario: Test model validation
      Given I have defined all domain models
      When I create test cases for model validation
      Then each model should have tests for valid data
      And each model should have tests for invalid data
      And confidence score validation should be tested (reject values < 0.0 or > 1.0)
      And optional fields should be tested with None values
      And enum/literal fields should reject invalid values
