Feature: User Login
  As a registered user
  I want to log in using my email and password
  So that I receive tokens for system authorization

  Background:
    Given the authentication system is available
    And a user with email "user@example.com" and password "ValidPass123" exists

  Scenario: Successfully login with valid credentials
    Given I am a registered user with email "user@example.com"
    When I login with email "user@example.com" and password "ValidPass123"
    Then the login should be successful
    And I should receive an access token
    And I should receive a refresh token
    And the token type should be "bearer"
    And the access token should expire in 15 minutes
    And the refresh token should expire in 1 day

  Scenario: Access token is a valid JWT signed with RS256
    Given I am a registered user with email "user@example.com"
    When I login with email "user@example.com" and password "ValidPass123"
    Then the login should be successful
    And the access token should be a valid JWT
    And the access token should be signed with RS256 algorithm
    And the access token should contain user identity information

  Scenario: Refresh token is stored in database with session
    Given I am a registered user with email "user@example.com"
    When I login with email "user@example.com" and password "ValidPass123"
    Then the login should be successful
    And the refresh token should be stored in the database as hash
    And the refresh token should have a session_id
    And the refresh token should not be revoked

  Scenario: Fail to login with incorrect password
    Given I am a registered user with email "user@example.com"
    When I login with email "user@example.com" and password "WrongPassword123"
    Then the login should fail with status 401
    And I should see an error message "Invalid credentials"
    And I should not receive any tokens

  Scenario: Fail to login with non-existent email
    Given I am a registered user
    When I login with email "nonexistent@example.com" and password "ValidPass123"
    Then the login should fail with status 401
    And I should see an error message "Invalid credentials"
    And I should not receive any tokens

  Scenario: Response contains all required token information
    Given I am a registered user with email "user@example.com"
    When I login with email "user@example.com" and password "ValidPass123"
    Then the login should be successful
    And the response should contain "access_token"
    And the response should contain "refresh_token"
    And the response should contain "token_type" with value "bearer"
    And the response should contain "expires_in" with value 900

