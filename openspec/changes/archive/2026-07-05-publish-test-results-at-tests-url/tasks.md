## 1. Test Report Generation

- [x] 1.1 Add pytest HTML reporting dependency if missing (for example `pytest-html`).
- [x] 1.2 Update Taskfile pytest tasks to generate HTML artifacts in a stable output directory.
- [x] 1.3 Ensure report output includes an index or report file suitable for browser viewing.

## 2. Server Route Exposure

- [x] 2.1 Add server configuration for a test report artifact directory path.
- [x] 2.2 Mount the report directory as static content at `/tests`.
- [x] 2.3 Ensure missing report files under `/tests` return not-found behavior.

## 3. Automated Verification

- [x] 3.1 Add tests verifying `/tests` serves generated report content.
- [x] 3.2 Add tests verifying `/tests` responds with not-found when artifacts are absent.
- [x] 3.3 Run test suite and confirm existing API behavior is unaffected.

## 4. Validation and Documentation

- [x] 4.1 Confirm OpenSpec artifacts reflect the final route and report directory contract.
- [x] 4.2 Run `openspec validate --changes publish-test-results-at-tests-url` and resolve any issues.
