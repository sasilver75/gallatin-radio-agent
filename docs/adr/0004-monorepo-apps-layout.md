# Use an apps-based monorepo layout

The project will use an apps-based monorepo layout with `apps/web` for the React/TypeScript frontend, `apps/api` for the FastAPI backend, optional shared schema artifacts under `packages/schemas`, and local infrastructure under `infra`. This keeps the demo deployable as one project while preserving clear ownership between UI, backend, schema, and infrastructure.
