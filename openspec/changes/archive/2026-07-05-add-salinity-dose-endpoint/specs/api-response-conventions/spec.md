## ADDED Requirements

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
