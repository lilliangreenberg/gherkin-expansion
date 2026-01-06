@passing
Feature: Claude API Integration

  As a developer
  I want to integrate with the Anthropic Claude API
  So that I can extract structured information from meeting transcripts

  Rule: API client must be properly configured

    Scenario: Initialize Claude API client
      Given I have an Anthropic API key in the environment variable ANTHROPIC_API_KEY
      When I initialize the Claude API client
      Then the client should be configured with claude-sonnet-4-5-20251101 as the primary model
      And the client should have a 60-second timeout
      And the client should be ready to make API calls

    Scenario: Handle missing API key
      Given the ANTHROPIC_API_KEY environment variable is not set
      When I attempt to initialize the Claude API client
      Then initialization should fail with message "ANTHROPIC_API_KEY environment variable not set"

  Rule: Structured extraction must use proper JSON schema

    Scenario: Define extraction JSON schema
      Given I am implementing structured extraction
      When I define the extraction JSON schema
      Then the schema should include fields for meeting metadata
      And the schema should include fields for decisions
      And the schema should include fields for action items with owners and deadlines
      And the schema should include fields for risks
      And the schema should include fields for next steps
      And the schema should include confidence scores for all extracted items
      And the schema should include ambiguity warnings

    Scenario: Perform structured extraction on meeting text
      Given a meeting transcript text
      And a properly configured Claude API client
      When I request structured extraction
      Then I should receive an ExtractionResult object
      And the result should contain validated meeting metadata
      And the result should contain a list of decisions
      And the result should contain a list of action items
      And the result should contain a list of risks
      And the result should contain a list of next steps
      And all items should have confidence scores

  Rule: Prompt engineering must be effective

    Scenario: Create system prompt for extraction
      Given I am implementing the extraction function
      When I create the system prompt
      Then it should include clear instructions for each extraction category
      And it should define urgency classification criteria
      And it should explain confidence scoring guidelines
      And it should describe ambiguity detection requirements
      And it should specify the expected output format
      And it should include edge case handling rules

    Scenario: Use temperature 0.0 for deterministic extraction
      Given I am making an API call for extraction
      When I configure the API parameters
      Then the temperature should be set to 0.0
      And the max_tokens should be set to 4096 by default

  Rule: Error handling must be robust

    Scenario: Handle API timeout
      Given the Claude API is slow to respond
      When the request exceeds the 60-second timeout
      Then the system should raise a timeout error
      And the error message should be user-friendly

    Scenario: Implement retry logic with exponential backoff
      Given the Claude API returns a transient error
      When I make the API call
      Then the system should retry up to 3 times
      And it should use exponential backoff between retries
      And it should succeed if a retry succeeds

    Scenario: Handle rate limit errors
      Given the Claude API returns a rate limit error
      When I make the API call
      Then the system should wait for the appropriate time
      And retry the request
      And inform the user about rate limiting

    Scenario: Handle invalid API response
      Given the Claude API returns malformed JSON
      When I process the response
      Then the system should raise a validation error
      And log the invalid response for debugging

    Scenario: Handle token limit exceeded
      Given a meeting transcript that exceeds token limits
      When I attempt to extract information
      Then the system should fail with message "Document too large for API"
      And suggest breaking the document into smaller parts

  Rule: Integration tests must use mocked API

    Scenario: Test extraction with mocked API responses
      Given I have created mock Claude API responses
      When I run the integration tests
      Then the tests should use mocked responses instead of real API calls
      And the mocks should simulate successful extractions
      And the mocks should simulate various error conditions
      And all error paths should be tested

    Scenario: Validate extraction result schema
      Given I receive a response from the Claude API
      When I parse the response
      Then the response should be validated against the ExtractionResult schema
      And any validation errors should be caught and reported
      And invalid confidence scores should be rejected
