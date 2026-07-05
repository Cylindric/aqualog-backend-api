## Why

The API can be run locally today, but there is no dedicated container definition for consistent execution in Docker-based workflows. Adding a Dockerfile now makes the service easier to build, run, and deploy in environments that expect a container image.

## What Changes

- Add a Dockerfile for the API server container.
- Define a module-based container startup command that starts the FastAPI application.
- Bake sane environment defaults into the image while allowing runtime environment overrides.
- Ensure the container image is suitable for local development and deployment workflows.
- Keep the container focused on running the API server, not on bundling unrelated tooling.

## Capabilities

### New Capabilities
- `api-container-image`: Builds a container image that can run the API server from a Dockerfile.

### Modified Capabilities
- None.

## Impact

- Build/deployment: introduces a Dockerfile and container runtime configuration.
- Developer workflow: enables container-based execution of the API server.
- Operational packaging: provides a consistent image definition for future orchestration or deployment.
