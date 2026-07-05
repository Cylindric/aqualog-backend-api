## Why

Coverage reports are currently generated in the terminal or local output directories, which makes them harder to inspect in a browser and share during development. Exposing the HTML coverage report from the running API server gives the team a quick visual way to review code coverage alongside test results.

## What Changes

- Add a browsable HTML coverage report directory generated from pytest coverage output.
- Expose the coverage report directory at `/coverage` when the server is running in development or test environments.
- Keep coverage output generation aligned with existing task-based test workflows.
- Add tests to verify `/coverage` serves the generated report and returns not-found for missing files.

## Capabilities

### New Capabilities
- `api-test-coverage-results-publishing`: Generates and serves pytest coverage HTML artifacts from a browsable server route.

### Modified Capabilities
- None.

## Impact

- Runtime API/server routing: adds a static mount or equivalent for `/coverage`.
- Test tooling: coverage task output should produce a stable HTML report directory.
- Dependencies: may require ensuring coverage HTML output is generated consistently by the task workflow.
- Developer workflow: coverage inspection becomes browser-accessible during local development and test runs.
