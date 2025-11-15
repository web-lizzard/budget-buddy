Feature: User Registration
  As a new user
  I want to register in the system using my email and password
  So that I can access the application

  Background:
    Given the registration system is available

  Scenario: Successfully register a new user with valid credentials
    Given I am a new user
    When I register with email "john.doe@example.com" and password "SecurePass123"
    Then the registration should be successful
    And my account should be active immediately
    And my password should be hashed in the database

  Scenario: Register with strong password meeting all requirements
    Given I am a new user
    When I register with email "alice@example.com" and password "MyStr0ngP@ss"
    Then the registration should be successful
    And the password should contain uppercase letters
    And the password should contain lowercase letters
    And the password should contain digits
    And the password should be at least 8 characters long

  Scenario: Fail to register with weak password - too short
    Given I am a new user
    When I register with email "bob@example.com" and password "Pass1"
    Then the registration should fail
    And I should see an error message "Password must be at least 8 characters long"

  Scenario: Fail to register with weak password - no uppercase letter
    Given I am a new user
    When I register with email "bob@example.com" and password "password123"
    Then the registration should fail
    And I should see an error message about missing uppercase letters

  Scenario: Fail to register with weak password - no lowercase letter
    Given I am a new user
    When I register with email "bob@example.com" and password "PASSWORD123"
    Then the registration should fail
    And I should see an error message about missing lowercase letters

  Scenario: Fail to register with weak password - no digits
    Given I am a new user
    When I register with email "bob@example.com" and password "PasswordOnly"
    Then the registration should fail
    And I should see an error message about missing digits

  Scenario: Fail to register with duplicate email address
    Given a user with email "existing@example.com" is already registered
    When I register with email "existing@example.com" and password "NewPass123"
    Then the registration should fail
    And I should see an error message "Email address already exists"

  Scenario: Fail to register with invalid email format
    Given I am a new user
    When I register with email "invalid-email" and password "ValidPass123"
    Then the registration should fail
    And I should see an error message about invalid email format

  Scenario: Password is properly hashed using secure algorithm
    Given I am a new user
    When I register with email "secure@example.com" and password "MySecure123"
    Then the registration should be successful
    And the password should be hashed using bcrypt or argon2
    And the plain password should not be stored in the database

