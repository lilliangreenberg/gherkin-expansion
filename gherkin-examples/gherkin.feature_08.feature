@passing
Feature: Batch Processing

  As a user
  I want to process multiple meeting files at once
  So that I can efficiently extract information from many meetings

  Rule: Multiple files must be processed sequentially

    Scenario: Process batch of multiple files
      Given I have 3 meeting files: "meeting1.pdf", "meeting2.md", "meeting3.txt"
      When I run batch processing
      Then each file should be processed in order
      And extraction results should be generated for each file
      And each file should be saved with a unique output filename

    Scenario: Display progress for batch processing
      Given I am processing 10 files
      When batch processing runs
      Then a progress indicator should be displayed
      And it should show current file number and total (e.g., "Processing 3/10")
      And it should show the current filename being processed
      And it should update in real-time

  Rule: Processing must continue on error

    Scenario: Continue batch processing after file error
      Given I have 5 files to process
      And file 2 will fail with an error
      When I run batch processing
      Then files 1 should be processed successfully
      And file 2 should fail with logged error
      And files 3, 4, and 5 should still be processed
      And the error should not stop the batch

    Scenario: Log failed files for retry
      Given a batch processing run with some failures
      When batch processing completes
      Then all failed files should be logged
      And the log should include the filename and error message
      And the log should be saved to a failed_files.log file

  Rule: Summary report must be generated after batch completion

    Scenario: Generate batch processing summary
      Given a batch of 10 files with 8 successes and 2 failures
      When batch processing completes
      Then a summary report should be displayed
      And it should show total files processed
      And it should show number of successes
      And it should show number of failures
      And it should show total processing time
      And it should list the failed files

    Scenario: Summary includes per-file statistics
      Given a completed batch processing run
      When I generate the summary
      Then it should show processing time for each file
      And it should show overall confidence for each file
      And it should highlight any low confidence extractions

  Rule: File queue management must be efficient

    Scenario: Build file processing queue from file list
      Given a list of files: ["meeting1.pdf", "meeting2.md", "meeting3.txt"]
      When I build the processing queue
      Then all files should be added to the queue
      And files should be validated before adding to queue
      And invalid files should be rejected with a message

    Scenario: Process files from glob pattern
      Given a glob pattern "meetings/*.pdf"
      And 5 PDF files in the meetings directory
      When I build the processing queue
      Then all 5 PDF files should be added to the queue
      And they should be sorted by filename

    Scenario: Handle empty file list
      Given an empty file list
      When I attempt to run batch processing
      Then an error should be raised
      And the message should be "No files to process"

  Rule: Parallel processing option (optional future enhancement)

    Scenario: Enable parallel processing with flag
      Given the --parallel flag is set
      And I have 10 files to process
      When I run batch processing
      Then multiple files should be processed concurrently
      And the number of parallel processes should be configurable
      And progress should be tracked for all concurrent processes

  Rule: Batch processing respects user review workflow

    Scenario: Review each file in batch when review is enabled
      Given batch processing of 3 files
      And review mode is enabled (default)
      When I process the batch
      Then after each extraction, results should be displayed for review
      And the user should be prompted to approve each file
      And the user can skip or approve each file individually

    Scenario: Skip review for entire batch with --no-review
      Given batch processing of 10 files
      And the --no-review flag is set
      When I process the batch
      Then all files should be processed without user prompts
      And all results should be saved automatically
      And only the final summary should be displayed

  Rule: Batch processing must handle mixed file types

    Scenario: Process batch with mixed file formats
      Given files: ["meeting1.pdf", "notes.md", "transcript.txt"]
      When I run batch processing
      Then each file should be processed using its appropriate handler
      And PDF files should be extracted with PDF handler
      And markdown files should be read directly
      And text files should be read directly
      And all results should be generated consistently

  Rule: Resource management during batch processing

    Scenario: Limit concurrent API calls to respect rate limits
      Given a batch of 20 files
      When batch processing runs
      Then API calls should be throttled appropriately
      And the system should wait between requests if needed
      And rate limit errors should be handled gracefully

    Scenario: Clean up temporary resources after each file
      Given batch processing is running
      When each file is processed
      Then temporary files should be cleaned up
      And memory should be freed
      And file handles should be closed
