## Purpose

Define standard success and error response envelopes and request-correlation behavior for API endpoints.

## Requirements

### Requirement: Successful API responses use a consistent envelope
The system SHALL return successful API responses using a consistent JSON envelope structure.

#### Scenario: Successful response includes envelope fields
- **WHEN** an API endpoint returns successful data
- **THEN** the response body contains the required success envelope fields and payload data

#### Scenario: Successful response declares JSON content type
- **WHEN** an API endpoint returns a successful response body
- **THEN** the response declares an application/json content type

### Requirement: Error responses use a standardized error envelope
The system MUST return errors using a standardized JSON envelope containing enough detail for client handling without exposing sensitive internals.

#### Scenario: Validation error returns standardized envelope
- **WHEN** client input fails request validation
- **THEN** the system returns a standardized error envelope with a client-actionable message

#### Scenario: Internal error returns sanitized message
- **WHEN** an unhandled server error occurs
- **THEN** the system returns a standardized error envelope with a generic safe message

### Requirement: Response envelope supports request correlation
The system SHALL include or reference a request correlation identifier in both success and error responses to support traceability.

#### Scenario: Success response includes correlation reference
- **WHEN** a successful response is returned
- **THEN** the response envelope includes a correlation identifier or reference field

#### Scenario: Error response includes correlation reference
- **WHEN** an error response is returned
- **THEN** the response envelope includes a correlation identifier or reference field

### Requirement: Salinity dose calculation endpoint uses standard response envelopes
The salinity dose calculation endpoint SHALL return success and error payloads using the same standardized API response envelopes as other endpoints.

#### Scenario: Successful salinity response uses success envelope
- **WHEN** `/calculate/dose/salinity` returns a computed salt quantity successfully
- **THEN** the response body uses the standard success envelope with the computed quantity in payload data

#### Scenario: Validation failure uses standardized error envelope
- **WHEN** `/calculate/dose/salinity` receives missing or invalid input parameters
- **THEN** the endpoint returns the standard error envelope with a client-actionable validation message

#### Scenario: Salinity responses include correlation reference
- **WHEN** `/calculate/dose/salinity` returns either success or error
- **THEN** the response envelope includes a correlation identifier or reference field

### Requirement: Serving coverage reports does not alter API response contracts
Serving coverage artifacts MUST NOT change established JSON envelope behavior of existing API endpoints.

#### Scenario: Existing API health endpoints remain unchanged
- **WHEN** health endpoints are requested after adding `/coverage` static serving
- **THEN** they continue returning the same status behavior and JSON envelope format
