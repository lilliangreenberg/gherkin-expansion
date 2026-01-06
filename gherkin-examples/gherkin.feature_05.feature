@passing
Feature: Extraction and Ranking Logic

  As a user
  I want action items to be ranked by urgency and have confidence scores
  So that I can prioritize the most important tasks from the meeting

  Rule: Urgency classification must be accurate

    Scenario: Classify action item with "urgent" keyword as High urgency
      Given an action item with text "We need to fix the bug URGENT"
      When I classify the urgency
      Then the urgency should be "High"

    Scenario: Classify action item with near deadline as High urgency
      Given an action item with deadline "tomorrow"
      When I classify the urgency
      Then the urgency should be "High"

    Scenario Outline: Classify urgency based on keywords
      Given an action item with text "<text>"
      When I classify the urgency
      Then the urgency should be "<urgency>"

      Examples:
        | text                                    | urgency |
        | Complete this ASAP                      | High    |
        | This is critical for the launch         | High    |
        | We should handle this soon              | Medium  |
        | This is important for next quarter      | Medium  |
        | Consider implementing this eventually   | Low     |
        | Nice to have feature                    | Low     |
        | Review the documentation                | Medium  |

    Scenario: Classify urgency based on deadline proximity
      Given today is "2024-01-15"
      And an action item with deadline "2024-01-16"
      When I classify the urgency
      Then the urgency should be "High"

    Scenario: Classify urgency with both keyword and deadline
      Given an action item with text "Important: complete by next week"
      And the action item has a deadline 7 days away
      When I classify the urgency
      Then the urgency should be "High"
      And the deadline should be weighted higher than the keyword

  Rule: Confidence scoring must be calculated correctly

    Scenario: Calculate overall confidence from item confidences
      Given an extraction result with 5 decisions with confidence [0.9, 0.85, 0.9, 0.95, 0.8]
      And 3 action items with confidence [0.75, 0.9, 0.85]
      When I calculate the overall confidence
      Then the overall confidence should be the average of all item confidences

    Scenario: Identify low confidence items
      Given a confidence threshold of 0.7
      And an extraction result with items having various confidence scores
      When I identify low confidence items
      Then all items with confidence < 0.7 should be flagged
      And they should be listed in the ambiguity warnings

  Rule: Deadline extraction must handle various formats

    Scenario Outline: Parse deadline from various date formats
      Given an action item with deadline text "<deadline_text>"
      When I extract the deadline
      Then the parsed date should be "<expected_date>"

      Examples:
        | deadline_text      | expected_date |
        | 2024-01-15        | 2024-01-15    |
        | January 15, 2024  | 2024-01-15    |
        | 01/15/2024        | 2024-01-15    |
        | next Friday       | (calculated)  |
        | end of month      | (calculated)  |
        | Q1 2024           | 2024-03-31    |

    Scenario: Handle missing deadline
      Given an action item without a deadline
      When I extract the deadline
      Then the deadline should be None
      And the urgency calculation should not depend on deadline

    Scenario: Handle ambiguous deadline
      Given an action item with deadline text "sometime next week"
      When I extract the deadline
      Then the confidence score should be lower
      And the deadline should be estimated conservatively

  Rule: Action items must be sorted by urgency

    Scenario: Sort action items by urgency level
      Given action items with urgencies [Low, High, Medium, High, Low]
      When I sort the action items
      Then the High urgency items should appear first
      And the Medium urgency items should appear second
      And the Low urgency items should appear last

    Scenario: Sort action items with same urgency by deadline
      Given two High urgency action items
      And one has a deadline of "2024-01-15"
      And one has a deadline of "2024-01-20"
      When I sort the action items
      Then the item with deadline "2024-01-15" should appear first

  Rule: Ambiguity detection must identify unclear content

    Scenario: Detect ambiguous action item without clear owner
      Given an action item "This should be done by someone"
      When I check for ambiguities
      Then an ambiguity warning should be added
      And the warning should mention "unclear owner"

    Scenario: Detect ambiguous deadline
      Given an action item with deadline "as soon as possible"
      When I check for ambiguities
      Then an ambiguity warning should be added
      And the warning should mention "ambiguous deadline"

    Scenario: Detect low confidence extractions
      Given an extraction result with items below confidence threshold
      When I check for ambiguities
      Then ambiguity warnings should be added for low confidence items
      And the warnings should include the item description and confidence score

  Rule: Validation rules must ensure data quality

    Scenario: Validate extracted data completeness
      Given an ExtractionResult
      When I validate the extraction
      Then all required fields should be present
      And confidence scores should be within valid range [0.0, 1.0]
      And urgency levels should be valid ("High", "Medium", or "Low")
      And dates should be valid datetime objects

    Scenario: Reject extraction with invalid confidence scores
      Given an extraction with a confidence score of 1.5
      When I validate the extraction
      Then validation should fail with message "Invalid confidence score"
