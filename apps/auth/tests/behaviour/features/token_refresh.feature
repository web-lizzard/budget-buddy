Feature: Token Refresh
  As a user with an expired access token
  I want to use my refresh token to obtain a new access token
  So that I can continue working without logging in again

  Background:
    Given the authentication system is available
    And a user with email "user@example.com" and password "ValidPass123" exists
    And the user is logged in with valid tokens

  Scenario: Successfully refresh access token with valid refresh token
    Given I have a valid refresh token
    When I request a new access token using the refresh token
    Then the refresh should be successful
    And I should receive a new access token
    And I should receive a new refresh token
    And the old refresh token should be marked as used
    And the new refresh token should have TTL of 1 day

  Scenario: Token rotation - old token cannot be reused
    Given I have a valid refresh token
    When I request a new access token using the refresh token
    Then the refresh should be successful
    And the old refresh token should be marked as used
    When I try to use the old refresh token again
    Then the refresh should fail with status 401
    And I should see an error message about invalid token

  Scenario: Fail to refresh with expired refresh token
    Given I have an expired refresh token
    When I request a new access token using the refresh token
    Then the refresh should fail with status 401
    And I should see an error message "Token expired"
    And I should not receive any tokens

  Scenario: Fail to refresh with revoked refresh token
    Given I have a revoked refresh token
    When I request a new access token using the refresh token
    Then the refresh should fail with status 401
    And I should see an error message "Token revoked"
    And I should not receive any tokens

  Scenario: Fail to refresh with non-existent refresh token
    Given I have an invalid refresh token
    When I request a new access token using the refresh token
    Then the refresh should fail with status 401
    And I should see an error message about invalid token
    And I should not receive any tokens

  Scenario: Validate refresh token in database
    Given I have a valid refresh token
    When I request a new access token using the refresh token
    Then the system should validate the token hash in database
    And the system should check token expiration
    And the system should check if token is revoked
    And the system should check if token is already used

  Scenario: New tokens have correct expiration times
    Given I have a valid refresh token
    When I request a new access token using the refresh token
    Then the refresh should be successful
    And the new access token should expire in 15 minutes
    And the new refresh token should expire in 1 day from now

