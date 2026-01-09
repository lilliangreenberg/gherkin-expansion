Feature: Multi-Channel Notification System

  As a system administrator
  I want to send notifications through multiple channels
  So that users receive important updates reliably

  Rule: Email notifications must be sent correctly

    Scenario: Send simple email notification
      Given a user with email "user@example.com"
      And email preferences are enabled
      When I send email notification with subject "Welcome" and body "Hello User"
      Then the email should be queued for delivery
      And the email should be sent within 5 minutes
      And the delivery status should be tracked

    Scenario: Email with HTML content and attachments
      Given a user with email "user@example.com"
      When I send email with HTML content and 2 attachments totaling 8MB
      Then the email should be formatted correctly
      And attachments should be encoded properly
      And the email size should not exceed 10MB limit

    Scenario: Reject email with attachments exceeding size limit
      Given a user with email "user@example.com"
      When I attempt to send email with attachments totaling 15MB
      Then the send should fail with message "Attachments exceed 10MB limit"
      And no email should be queued

    Scenario: Handle invalid email addresses gracefully
      Given an invalid email address "not-an-email"
      When I attempt to send notification
      Then the send should fail with message "Invalid email address format"
      And the error should be logged

    Scenario: Retry failed email delivery
      Given an email that failed to send due to temporary error
      When the retry mechanism executes
      Then the email should be retried up to 3 times
      And the retry delays should increase exponentially (1min, 5min, 15min)
      And after 3 failures, the email should be marked as permanently failed

  Rule: SMS notifications must respect carrier limits

    Scenario: Send SMS notification within character limit
      Given a user with phone number "+1234567890"
      And SMS preferences are enabled
      When I send SMS with 150 characters
      Then the SMS should be sent as single message
      And the delivery should be confirmed

    Scenario: Split long SMS into multiple messages
      Given a user with phone number "+1234567890"
      When I send SMS with 300 characters
      Then the SMS should be split into 2 messages
      And messages should be numbered (1/2, 2/2)
      And messages should be sent in correct order

    Scenario: Reject SMS to invalid phone number
      Given an invalid phone number "123"
      When I attempt to send SMS notification
      Then the send should fail with message "Invalid phone number format"
      And no SMS should be sent

    Scenario: Handle unsubscribed phone numbers
      Given a user with phone number "+1234567890"
      And the user has unsubscribed from SMS notifications
      When I attempt to send SMS notification
      Then the SMS should not be sent
      And the attempt should be logged with reason "User unsubscribed"

  Rule: Push notifications must handle device states

    Scenario: Send push notification to active device
      Given a user with registered device token "ABC123"
      And the device is active
      When I send push notification "New message received"
      Then the notification should be delivered immediately
      And the device should display the notification

    Scenario: Queue push notification for offline device
      Given a user with registered device token "ABC123"
      And the device is offline
      When I send push notification "New message received"
      Then the notification should be queued
      And it should be delivered when device comes online
      And the notification should expire after 7 days if not delivered

    Scenario: Remove invalid device tokens
      Given a user with device token "INVALID123"
      And the device token is no longer valid
      When I attempt to send push notification
      Then the device token should be marked as invalid
      And it should be removed from user's devices
      And an error should be logged

    Scenario: Send push to multiple devices
      Given a user with 3 registered devices
      When I send push notification "Account logged in from new device"
      Then all 3 devices should receive the notification
      And delivery should be tracked per device
      And partial failures should not prevent other deliveries

  Rule: Rate limiting must prevent notification spam

    Scenario: Allow notifications within rate limit
      Given a user with standard rate limit of 100 notifications per hour
      And the user has received 50 notifications in the last hour
      When I send a notification
      Then the notification should be sent
      And the rate limit counter should be incremented

    Scenario: Block notifications exceeding rate limit
      Given a user with rate limit of 100 notifications per hour
      And the user has received 100 notifications in the last hour
      When I attempt to send a notification
      Then the notification should be blocked
      And I should receive message "Rate limit exceeded, try again in X minutes"
      And the blocked attempt should be logged

    Scenario: Rate limit resets after time window
      Given a user exceeded rate limit 61 minutes ago
      When I attempt to send a notification
      Then the notification should be sent
      And the rate limit counter should be reset

    Scenario: Critical notifications bypass rate limiting
      Given a user has exceeded their rate limit
      When I send a critical notification with priority "HIGH"
      Then the notification should be sent regardless of rate limit
      And the notification should be marked as critical

  Rule: Notification preferences must be respected

    Scenario: Respect channel-specific preferences
      Given a user with email notifications enabled
      And SMS notifications disabled
      When I send notification to all channels
      Then the email should be sent
      And the SMS should not be sent
      And the preference should be logged

    Scenario: Respect quiet hours setting
      Given a user with quiet hours set to 10 PM - 7 AM
      And current time is 11 PM
      When I send a non-urgent notification
      Then the notification should be queued
      And it should be delivered at 7 AM
      And urgent notifications should override quiet hours

    Scenario: Respect notification category preferences
      Given a user subscribed to "Account" notifications
      And unsubscribed from "Marketing" notifications
      When I send a marketing notification
      Then the notification should not be sent
      And the preference should be recorded

  Rule: Notification delivery must be tracked and auditable

    Scenario: Track notification lifecycle
      Given I send an email notification
      Then the status should progress through stages
      And I should see status "queued" initially
      And I should see status "sent" after delivery
      And I should see status "delivered" when confirmed
      And each status change should be timestamped

    Scenario: Handle bounce notifications
      Given I sent email to "bounced@example.com"
      And the email bounces
      When the bounce notification is received
      Then the email should be marked as "bounced"
      And the bounce reason should be recorded
      And after 3 consecutive bounces, the email should be marked as invalid

    Scenario: Track user engagement with notifications
      Given I sent push notification with action buttons
      When the user clicks "View Details" button
      Then the click should be tracked
      And the notification should be marked as "engaged"
      And analytics should record the action

  Rule: Bulk notifications must be efficient

    Scenario: Send notification to 10,000 users efficiently
      Given I have 10,000 users to notify
      When I trigger bulk notification
      Then notifications should be queued in batches of 100
      And processing should be parallelized
      And the bulk job should complete within 30 minutes
      And progress should be trackable

    Scenario: Handle partial failures in bulk sending
      Given I am sending to 1,000 users
      And 50 users have invalid contact details
      When the bulk send completes
      Then 950 notifications should be sent successfully
      And 50 failures should be recorded with reasons
      And I should receive summary report

    Scenario: Throttle bulk sends to prevent service overload
      Given I am sending to 100,000 users
      When bulk send starts
      Then the send rate should not exceed 1,000 per minute
      And the throttling should prevent API rate limits
      And estimated completion time should be displayed
