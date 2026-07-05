## ADDED Requirements

### Requirement: Pytest coverage HTML report artifacts are generated to a browsable directory
The system SHALL generate pytest coverage artifacts as HTML files in a stable output directory suitable for static hosting.

#### Scenario: Coverage task writes HTML report
- **WHEN** the designated coverage task is executed
- **THEN** an HTML coverage report file is written to the configured report output directory

#### Scenario: Coverage assets are colocated with HTML output
- **WHEN** the HTML coverage report is generated with supporting assets
- **THEN** all required files are stored under the same browsable report directory tree

### Requirement: Coverage report directory is served at `/coverage`
The running service SHALL expose the coverage report directory at URL path `/coverage` for browser access.

#### Scenario: Coverage route is enabled for development and test environments
- **WHEN** the service runs with `app_env` set to `dev` or `test`
- **THEN** `/coverage` is mounted and serves report content from the configured coverage report directory

#### Scenario: Coverage route is disabled outside development and test environments
- **WHEN** the service runs with `app_env` set to an environment other than `dev` or `test`
- **THEN** `/coverage` is not mounted

#### Scenario: Coverage route serves generated report content
- **WHEN** a client requests `/coverage` or a file under `/coverage`
- **THEN** the server responds with static coverage report content from the configured report directory

#### Scenario: Missing coverage report files return not found
- **WHEN** a requested coverage report file does not exist in the report directory
- **THEN** the server returns a not-found response

### Requirement: Serving coverage reports does not alter API response contracts
Serving coverage artifacts MUST NOT change established JSON envelope behavior of existing API endpoints.

#### Scenario: Existing API health endpoints remain unchanged
- **WHEN** health endpoints are requested after adding `/coverage` static serving
- **THEN** they continue returning the same status behavior and JSON envelope format
