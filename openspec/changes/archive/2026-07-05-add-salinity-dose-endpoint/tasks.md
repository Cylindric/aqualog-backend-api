## 1. API Endpoint Implementation

- [x] 1.1 Add route and handler for `/calculate/dose/salinity` under the versioned API namespace.
- [x] 1.2 Accept and validate required input parameters `volume`, `current`, and `target`.
- [x] 1.3 Implement dose calculation using `(target - current) * 1.1 * volume`.
- [x] 1.4 Return calculation results using the standard success response envelope.

## 2. Error Handling and Response Conventions

- [x] 2.1 Return standardized error envelopes for missing or invalid parameters.
- [x] 2.2 Ensure correlation identifier/reference is present in success and error responses for the endpoint.

## 3. Test Coverage

- [x] 3.1 Add endpoint tests for successful dose calculation with representative numeric inputs.
- [x] 3.2 Add endpoint tests for validation failures (missing/non-numeric parameters).
- [x] 3.3 Verify all new tests pass with existing response and bootstrap test suites.

## 4. Documentation and Verification

- [x] 4.1 Confirm endpoint contract and formula behavior are reflected in OpenSpec delta specs.
- [x] 4.2 Run OpenSpec validation for `add-salinity-dose-endpoint` and address any issues.
