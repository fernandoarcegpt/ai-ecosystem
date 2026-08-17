# Test OpenSpec

## Requirement: User authentication

The system SHALL support secure user authentication with token-based sessions.

### Scenario: Default session timeout
- GIVEN a user has authenticated
- WHEN 24 hours pass without activity
- THEN invalidate the session token

### Scenario: Extended session with remember me
- GIVEN user checks "Remember me" at login
- WHEN 30 days have passed
- THEN invalidate the session token
- AND clear the persistent cookie