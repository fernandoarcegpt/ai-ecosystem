# User Authentication

### Requirement: Session management
- The system SHALL manage user sessions securely.

#### Scenario: Login
- GIVEN a user has valid credentials
- WHEN they submit login form
- THEN authenticate and create session
- AND set secure session cookie

#### Scenario: Session expiration
- GIVEN a user has authenticated
- WHEN session timeout is reached
- THEN invalidate session token
- AND redirect to login
