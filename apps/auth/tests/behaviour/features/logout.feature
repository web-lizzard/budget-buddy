Feature: Logout and Token Revocation
  As a user
  I want to be able to log out of the application
  So that I can protect my account after finishing work

  Background:
    Given the authentication system is available
    And a user with email "user@example.com" and password "ValidPass123" exists
    And the user is logged in with valid tokens

  Scenario: Successfully logout and invalidate tokens
    Given I am logged in with valid tokens
    When I logout with my refresh token
    Then the logout should be successful
    And my refresh token should be marked as revoked
    And I should see a message "Logged out successfully"

  Scenario: Cannot use access token after logout
    Given I am logged in with valid tokens
    When I logout with my refresh token
    Then the logout should be successful
    And my access token should be added to blacklist in Redis
    And the blacklist key should be "blacklist:{jti}"
    And the blacklist TTL should match token expiration

  Scenario: Cannot use refresh token after logout
    Given I am logged in with valid tokens
    When I logout with my refresh token
    Then the logout should be successful
    And my refresh token should be revoked
    When I try to use the refresh token again
    Then the refresh should fail with status 401
    And I should see an error message about revoked token

  Scenario: Logout is idempotent - already logged out token
    Given I am logged in with valid tokens
    And I have already logged out
    When I logout with the same refresh token again
    Then the logout should return status 200
    And I should see a message "Logged out successfully"

  Scenario: Logout is idempotent - expired token
    Given I have an expired refresh token
    When I logout with the expired refresh token
    Then the logout should return status 200
    And I should see a message "Logged out successfully"

  Scenario: Logout marks revoked_at timestamp
    Given I am logged in with valid tokens
    When I logout with my refresh token
    Then the logout should be successful
    And the refresh token should have revoked_at timestamp set to now
    And the revoked_at timestamp should be stored in UTC

  Scenario: Multiple device logout
    Given I am logged in on multiple devices
    And each device has a different refresh token
    When I logout from one device
    Then only that device's refresh token should be revoked
    And other devices should remain logged in
    And I can still use tokens from other devices

