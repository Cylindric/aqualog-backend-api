## Why

The API currently lacks a dedicated salinity dose calculation endpoint, requiring clients to duplicate business logic and risking inconsistent results. Adding a standardized endpoint now improves correctness and keeps dosing calculations centralized.

## What Changes

- Add a new API endpoint at `/calculate/dose/salinity`.
- Accept calculation inputs: `volume`, `current`, and `target`.
- Return the computed quantity of salt to add using `(target - current) * 1.1 * volume`.
- Validate request parameters and return standardized error responses for invalid input.
- Add automated tests for successful calculation and validation failures.

## Capabilities

### New Capabilities
- `api-salinity-dose-calculation`: Provides a salinity dosing calculation endpoint and response contract.

### Modified Capabilities
- `api-response-conventions`: Clarify that the new dosing endpoint uses the standardized success and error envelopes.

## Impact

- API surface: Adds one new endpoint under the existing versioned API namespace.
- Application code: Route registration and calculation handling in the API layer.
- Tests: New endpoint behavior and validation coverage.
- Client integrations: Clients can rely on a server-side canonical salinity dose calculation.
