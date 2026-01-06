@passing
Feature: File Processing Infrastructure

  As a user
  I want the tool to read and validate meeting files
  So that I can extract information from PDF, Markdown, and text files

  Rule: File validation must check size and format

    Scenario: Validate file size within limit
      Given a file named "meeting.pdf" with size 3MB
      When I validate the file
      Then the validation should succeed

    Scenario: Reject file exceeding size limit
      Given a file named "large_meeting.pdf" with size 7MB
      When I validate the file
      Then the validation should fail with message "File exceeds maximum size of 5MB"

    Scenario: Validate supported file formats
      Given a file named "meeting.pdf"
      When I validate the file format
      Then the validation should succeed

    Scenario Outline: Validate various file formats
      Given a file named "<filename>"
      When I validate the file format
      Then the validation should <result>

      Examples:
        | filename        | result  |
        | meeting.pdf     | succeed |
        | notes.md        | succeed |
        | transcript.txt  | succeed |
        | meeting.docx    | fail    |
        | audio.mp3       | fail    |
        | video.mp4       | fail    |
        | image.jpg       | fail    |

  Rule: PDF text extraction must work reliably

    Scenario: Extract text from text-based PDF
      Given a text-based PDF file "meeting.pdf"
      When I extract text from the PDF
      Then I should receive the full text content
      And the text should maintain reasonable formatting
      And the text should be UTF-8 encoded

    Scenario: Handle scanned PDF without OCR
      Given a scanned PDF file "scanned_meeting.pdf"
      When I attempt to extract text from the PDF
      Then the extraction should fail with message "PDF appears to be scanned; OCR not supported"

    Scenario: Handle corrupted PDF file
      Given a corrupted PDF file "broken.pdf"
      When I attempt to extract text from the PDF
      Then the extraction should fail with a clear error message

  Rule: Markdown and text files must be read correctly

    Scenario: Read markdown file with UTF-8 encoding
      Given a markdown file "notes.md" with UTF-8 content
      When I read the markdown file
      Then I should receive the full text content
      And special characters should be preserved

    Scenario: Read plain text file
      Given a plain text file "transcript.txt"
      When I read the text file
      Then I should receive the full text content

    Scenario: Handle encoding detection
      Given a file with non-UTF-8 encoding
      When I attempt to read the file
      Then the system should detect the encoding
      And convert it to UTF-8

  Rule: Language detection must validate English content

    Scenario: Accept English language content
      Given a file with English text content
      When I validate the language
      Then the validation should succeed

    Scenario: Reject non-English content
      Given a file with Spanish text content
      When I validate the language
      Then the validation should fail with message "Only English language content is supported"

    Scenario: Handle mixed-language content
      Given a file with mostly English but some non-English phrases
      When I validate the language
      Then the validation should succeed if English is predominant

  Rule: File processing must be abstracted properly

    Scenario: Process file through unified interface
      Given any supported file type
      When I process the file through the FileProcessor interface
      Then I should receive extracted text content
      And I should receive file metadata (name, size, type)
      And any errors should be wrapped in appropriate exceptions

    Scenario: Test all file types through abstraction
      Given the FileProcessor abstraction is implemented
      When I create test cases for all file types
      Then PDF processing should be tested
      And Markdown processing should be tested
      And plain text processing should be tested
      And error cases should be tested for each type
