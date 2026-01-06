@passing
Feature: User Review Workflow

  As a user
  I want to review extracted information before it's saved
  So that I can verify accuracy and make corrections if needed

  Rule: Extracted content must be displayed in formatted terminal output

    Scenario: Display extraction results in terminal
      Given an ExtractionResult with all sections populated
      When I display the results in the terminal
      Then I should see a formatted display of meeting metadata
      And I should see all decisions with their context
      And I should see all action items in a table format
      And I should see all risks with severity
      And I should see all next steps
      And the output should be readable and well-organized

    Scenario: Display confidence scores for each section
      Given an ExtractionResult with confidence scores
      When I display the results in the terminal
      Then each decision should show its confidence score
      And each action item should show its confidence score
      And each risk should show its confidence score
      And each next step should show its confidence score
      And the overall confidence should be displayed

    Scenario: Highlight low confidence items
      Given an ExtractionResult with some low confidence items
      And a confidence threshold of 0.7
      When I display the results in the terminal
      Then items with confidence < 0.7 should be visually highlighted
      And they should be marked with a warning indicator
      And a summary of low confidence items should be shown

  Rule: User must be prompted for confirmation

    Scenario: Prompt user to approve extraction results
      Given extraction results are displayed in the terminal
      When I prompt the user for approval
      Then I should show a clear "Save these results? (Y/n)" prompt
      And I should wait for user input
      And the default option should be "Yes"

    Scenario: User approves results
      Given extraction results are displayed
      When the user enters "Y" or presses Enter
      Then the approval should be confirmed
      And the results should proceed to be saved

    Scenario: User rejects results
      Given extraction results are displayed
      When the user enters "n"
      Then the approval should be rejected
      And the results should not be saved
      And a message should confirm cancellation

  Rule: Low confidence warnings must be clear

    Scenario: Show warning banner for low confidence extraction
      Given an ExtractionResult with overall confidence of 0.65
      And a confidence threshold of 0.7
      When I display the results
      Then a prominent warning banner should be shown at the top
      And it should state "Low confidence extraction - please review carefully"
      And it should list the number of low confidence items

    Scenario: List all low confidence items in summary
      Given multiple low confidence items across different sections
      When I display the results
      Then a "Low Confidence Items" section should be shown
      And it should list each low confidence item with its section
      And it should show the confidence score for each

  Rule: Review can be skipped with flag

    Scenario: Skip review with --no-review flag
      Given the --no-review flag is set
      When extraction completes
      Then the review workflow should be bypassed
      And results should be saved automatically
      And a message should confirm auto-save

    Scenario: Force processing with low confidence
      Given an extraction has low confidence
      And the --force flag is set
      When I process the file
      Then the extraction should proceed despite low confidence
      And a warning should be logged about forced processing

  Rule: Optional editing before save

    Scenario: Allow user to edit before saving (future enhancement)
      Given extraction results are displayed
      And an --allow-edit flag is set
      When the user chooses to edit
      Then an interactive editor should open
      And the user should be able to modify the extracted content
      And modified results should be validated before saving

  Rule: Display formatting must use rich terminal features

    Scenario: Use colors and formatting for better readability
      Given extraction results are being displayed
      When I render the output
      Then section headers should be bold and colored
      And high urgency items should be shown in red
      And medium urgency items should be shown in yellow
      And low urgency items should be shown in green
      And confidence scores should be color-coded

    Scenario: Display action items as a formatted table
      Given a list of action items
      When I display them in the terminal
      Then they should be shown in a table with columns: Urgency, Task, Owner, Deadline, Confidence
      And the table should be properly aligned
      And the table should have borders and headers

    Scenario: Handle terminal width gracefully
      Given a terminal with limited width
      When I display extraction results
      Then long text should be wrapped appropriately
      And table columns should be adjusted to fit
      And the display should remain readable
