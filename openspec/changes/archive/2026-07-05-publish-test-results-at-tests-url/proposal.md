## Why

Test execution currently provides terminal output only, which makes result review difficult for non-terminal workflows and remote inspection. Publishing pytest HTML results at a stable route enables faster debugging and shared visibility while the server is running.

## What Changes

- Add a browsable test results directory generated from pytest HTML reports.
- Add/update pytest tasks to produce HTML result files in a predictable output path.
- Expose the generated report directory at URL path `/tests` from the running server.
- Ensure `/tests` serves index/report files and static assets needed for HTML viewing.
- Add tests for route availability and behavior when report files exist.

## Capabilities

### New Capabilities
- `api-test-results-publishing`: Generates and serves pytest HTML artifacts from a browsable server route.

### Modified Capabilities
- None.

## Impact

- Runtime API/server routing: adds a static mount or equivalent for `/tests`.
- Test tooling: pytest task updates for HTML output generation.
- Dependencies: may require pytest HTML reporting plugin if not already present.
- Documentation: test execution and report viewing workflow should be clarified.
