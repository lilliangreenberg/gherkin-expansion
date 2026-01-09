Feature: User Authentication and Session Management

  As a user
  I want to securely authenticate and manage my session
  So that I can access my account safely

  Rule: User login must validate credentials properly

    Scenario: Successful login with valid credentials
      Given a registered user with email "user@example.com" and password "SecurePass123!"
      When I attempt to login with email "user@example.com" and password "SecurePass123!"
      Then the login should succeed
      And I should receive a valid session token
      And the token should expire in 24 hours

    Scenario: Failed login with incorrect password
      Given a registered user with email "user@example.com"
      When I attempt to login with email "user@example.com" and password "WrongPassword"
      Then the login should fail with message "Invalid email or password"
      And no session token should be issued
      And the failed attempt should be logged

    Scenario: Failed login with non-existent email
      Given no user exists with email "nonexistent@example.com"
      When I attempt to login with email "nonexistent@example.com" and password "AnyPassword"
      Then the login should fail with message "Invalid email or password"
      And the response time should be consistent with valid user attempts

    Scenario: Account lockout after multiple failed attempts
      Given a registered user with email "user@example.com"
      And the user has made 4 failed login attempts in the last 10 minutes
      When I attempt to login with incorrect password
      Then the account should be locked
      And the login should fail with message "Account temporarily locked due to multiple failed attempts"
      And the lockout should expire after 30 minutes

  Rule: Password validation must enforce security requirements

    Scenario Outline: Password strength validation
      Given I am creating a new account
      When I provide password "<password>"
      Then the validation should <result>

      Examples:
        | password           | result  |
        | SecurePass123!     | succeed |
        | short              | fail    |
        | nouppercasepass1!  | fail    |
        | NOLOWERCASEPASS1!  | fail    |
        | NoSpecialChar123   | fail    |
        | NoNumbers!Pass     | fail    |
        | P@ssw0rd           | succeed |
        | MyV3ry$ecureP@ss   | succeed |

  Rule: Session management must handle edge cases

    Scenario: Session token expires after 24 hours
      Given I logged in 24 hours and 1 minute ago
      When I attempt to access a protected resource
      Then the request should fail with message "Session expired"
      And I should be redirected to login page

    Scenario: Concurrent sessions from different devices
      Given I am logged in on device A
      When I login from device B
      Then both sessions should remain valid
      And each session should have unique tokens
      And I can logout from one device without affecting the other

    Scenario: Token refresh before expiration
      Given I have a valid session token expiring in 2 hours
      When I request a token refresh
      Then I should receive a new token
      And the new token should expire in 24 hours from now
      And the old token should be invalidated

    Scenario: Invalid or tampered session token
      Given I have a session token
      When I modify the token signature
      And I attempt to access a protected resource
      Then the request should fail with message "Invalid session token"
      And the tampering attempt should be logged

  Rule: Password reset must be secure

    Scenario: Request password reset with valid email
      Given a registered user with email "user@example.com"
      When I request a password reset for "user@example.com"
      Then a reset token should be generated
      And a reset email should be sent to "user@example.com"
      And the token should expire in 1 hour

    Scenario: Request password reset with non-existent email
      Given no user exists with email "nonexistent@example.com"
      When I request a password reset for "nonexistent@example.com"
      Then the response should indicate "Reset email sent if account exists"
      And no email should actually be sent
      And the response time should be consistent with valid requests

    Scenario: Use expired password reset token
      Given I requested a password reset 2 hours ago
      When I attempt to reset password using the expired token
      Then the request should fail with message "Reset token has expired"
      And I should be prompted to request a new reset

    Scenario: Reset token can only be used once
      Given I have a valid password reset token
      When I successfully reset my password using the token
      And I attempt to use the same token again
      Then the request should fail with message "Reset token has already been used"

  Rule: Account security features must prevent abuse

    Scenario: Rate limiting on login attempts
      Given I am not logged in
      When I make 100 login attempts within 1 minute
      Then after 10 attempts, subsequent requests should be rate limited
      And I should receive message "Too many requests, please try again later"
      And the rate limit should reset after 5 minutes

    Scenario: Detection of unusual login location
      Given a user typically logs in from United States
      When a login attempt is made from Russia
      Then the login should require additional verification
      And an email notification should be sent to the user
      And the user should confirm the login via email link

    Scenario: Session invalidation on password change
      Given I am logged in with active sessions on 3 devices
      When I change my password
      Then all existing sessions should be invalidated
      And I should need to login again on all devices
      And I should receive confirmation email about password change
