Feature: Automatic Session Expiration
  As a user
  I want my session to automatically expire after a period of inactivity
  So that my account security is enhanced

  Background:
    Given the authentication system is available
    And a user with email "user@example.com" and password "ValidPass123" exists

  Scenario: Access token expires after 15 minutes
    Given I am logged in with valid tokens
    When 15 minutes pass
    Then my access token should be expired
    And I should need to use refresh token to continue

  Scenario: Refresh token expires after 1 day
    Given I am logged in with valid tokens
    When 1 day passes
    Then my refresh token should be expired
    And I should need to log in again

  Scenario: User must re-login after refresh token expiration
    Given I am logged in with valid tokens
    And my refresh token has expired
    When I try to refresh my access token
    Then the refresh should fail with status 401
    And I should need to provide credentials again

  Scenario: Cleanup job removes expired tokens older than 7 days
    Given there are expired refresh tokens older than 7 days in the database
    When the cleanup job runs
    Then all expired tokens older than 7 days should be removed from database
    And recent expired tokens should be kept for audit purposes

  Scenario: Cleanup job runs every 24 hours
    Given the cleanup job is scheduled
    Then the job should run every 24 hours
    And the job should remove tokens expired more than 7 days ago
    And the job should log the number of tokens removed

