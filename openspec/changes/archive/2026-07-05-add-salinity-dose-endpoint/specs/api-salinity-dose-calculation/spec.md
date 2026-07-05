## ADDED Requirements

### Requirement: Salinity dose calculation endpoint is available
The system SHALL expose an HTTP endpoint at `/calculate/dose/salinity` for salinity dosing calculations.

#### Scenario: Endpoint is routable
- **WHEN** a client sends a request to `/calculate/dose/salinity`
- **THEN** the API processes the request using the salinity dosing calculation handler

### Requirement: Salinity dose calculation accepts required inputs
The endpoint MUST accept `volume`, `current`, and `target` as required calculation parameters.

#### Scenario: Valid inputs are accepted
- **WHEN** `volume`, `current`, and `target` are provided with valid numeric values
- **THEN** the endpoint accepts the request for dose calculation

#### Scenario: Missing or invalid inputs are rejected
- **WHEN** one or more required parameters are missing or non-numeric
- **THEN** the endpoint returns a client error response indicating invalid request input

### Requirement: Salinity dose is computed using canonical formula
The system SHALL compute required salt quantity using `(target - current) * 1.1 * volume`.

#### Scenario: Calculation returns expected quantity
- **WHEN** valid `volume`, `current`, and `target` values are submitted
- **THEN** the response includes a salt quantity equal to `(target - current) * 1.1 * volume`

#### Scenario: No additional adjustment factors are applied
- **WHEN** a dose calculation request is processed
- **THEN** the returned quantity is derived only from `target`, `current`, `volume`, and multiplier `1.1`
