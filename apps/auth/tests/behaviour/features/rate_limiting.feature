Feature: Rate Limiting for Authentication Endpoints
  As a security system
  I want to limit the number of login attempts from the same IP
  So that I can protect against brute-force attacks

  Background:
    Given the authentication system is available
    And a user with email "user@example.com" and password "ValidPass123" exists
    And rate limiting is enabled

  Scenario: Allow up to 5 failed login attempts within 15 minutes
    Given I am attempting to login from IP "192.168.1.100"
    When I make 5 failed login attempts
    Then all attempts should be processed
    And I should receive 401 responses for each attempt

  Scenario: Block login attempts after 5 failures within 15 minutes
    Given I am attempting to login from IP "192.168.1.100"
    And I have made 5 failed login attempts
    When I make another login attempt
    Then the request should be blocked with status 429
    And I should see an error message "Too many login attempts, please try again in X minutes"
    And the response should include Retry-After header

  Scenario: Temporary ban lasts 15 minutes from last attempt
    Given I am attempting to login from IP "192.168.1.100"
    And I have exceeded the rate limit
    When 14 minutes pass
    And I try to login again
    Then the request should still be blocked with status 429
    When 1 more minute passes
    And I try to login again
    Then the request should be allowed

  Scenario: Rate limit is tracked in Redis by IP address
    Given I am attempting to login from IP "192.168.1.100"
    When I make a failed login attempt
    Then a Redis key "rate_limit:login:192.168.1.100" should be created
    And the key should have a TTL of 15 minutes
    And the key value should be incremented

  Scenario: Successful login resets the rate limit counter
    Given I am attempting to login from IP "192.168.1.100"
    And I have made 3 failed login attempts
    When I make a successful login attempt
    Then the rate limit counter for my IP should be reset
    And I should be able to make 5 more failed attempts

  Scenario: Retry-After header indicates time until next attempt
    Given I am attempting to login from IP "192.168.1.100"
    And I have exceeded the rate limit at timestamp T
    When I make another login attempt at timestamp T+5min
    Then the response should include Retry-After header
    And the Retry-After value should indicate approximately 10 minutes

  Scenario: Different IP addresses have independent rate limits
    Given user "alice@example.com" attempts login from IP "192.168.1.100"
    And user "bob@example.com" attempts login from IP "192.168.1.101"
    When "192.168.1.100" makes 5 failed login attempts
    Then "192.168.1.100" should be rate limited
    But "192.168.1.101" should not be affected
    And "192.168.1.101" can make 5 failed attempts independently

  Scenario: Rate limit applies to login endpoint only
    Given I am attempting to login from IP "192.168.1.100"
    And I have exceeded the rate limit for login
    When I access the token refresh endpoint
    Then the request should not be blocked by rate limiting
    And rate limiting should be specific to login endpoint

  Scenario: Rate limit counter expires after 15 minutes
    Given I am attempting to login from IP "192.168.1.100"
    And I have made 4 failed login attempts
    When 15 minutes pass
    Then the rate limit counter should expire
    And I should be able to make 5 new failed attempts
    And the Redis key should be automatically deleted

