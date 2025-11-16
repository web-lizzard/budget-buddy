Feature: Token Theft Detection
  As a security system
  I want to detect attempts to reuse already-used refresh tokens
  So that I can identify potential attacks and protect user accounts

  Background:
    Given the authentication system is available
    And a user with email "victim@example.com" and password "ValidPass123" exists
    And the user is logged in with valid tokens

  Scenario: Detect reuse of already-used refresh token
    Given I have a valid refresh token
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then the system should detect token reuse
    And a security warning should be logged
    And the log should include IP address
    And the log should include user agent
    And the log should include timestamp
    And the log should include user_id
    And the log should include token_id
    And the refresh should fail with status 401

  Scenario: Security log contains information about potential incident
    Given I have a valid refresh token
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then a security log with WARNING level should be created
    And the log should contain information about potential security incident
    And the log message should indicate token reuse attempt

  Scenario: Increment metrics counter on token reuse detection
    Given I have a valid refresh token
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then the metric "refresh_token_reuse_detected" should be incremented
    And the system should track reuse attempts for monitoring

  Scenario: Invalidate entire token family when reuse is detected
    Given I have a valid refresh token from session "session-123"
    And I have used the refresh token to get new tokens
    And I have multiple active tokens in the same session
    When someone tries to use the old refresh token again
    Then all tokens with session_id "session-123" should be revoked
    And both attacker and legitimate user should need to re-login
    And an ERROR level security incident should be logged

  Scenario: Return appropriate error message on token reuse
    Given I have a valid refresh token
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then the refresh should fail with status 401
    And the error message should be "Token reuse detected - session invalidated"

  Scenario: Audit log tracks token family invalidation
    Given I have a valid refresh token from session "session-456"
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then an ERROR level audit log should be created
    And the audit log should contain session_id "session-456"
    And the audit log should indicate all tokens in family were revoked
    And the audit log should contain the reason "token reuse detected"

  Scenario: Optional email notification on suspicious activity
    Given I have a valid refresh token
    And email notifications are enabled
    And I have used the refresh token to get new tokens
    When someone tries to use the old refresh token again
    Then an email notification should be sent to the user
    And the email should warn about suspicious activity
    And the email should advise the user to change their password

