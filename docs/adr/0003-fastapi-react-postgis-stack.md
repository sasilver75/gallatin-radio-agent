# Use FastAPI, React, PostGIS, and MapLibre for the v1 demo

The v1 demo will use a React/TypeScript frontend with a Python FastAPI backend. Python is a better fit for the geospatial, audio, routing, and LLM-orchestration work, while React/TypeScript keeps the map-first operator UI fast to build; OpenAPI will serve as the contract between the two.

**Consequences**

The backend will use explicit Pydantic schemas and expose OpenAPI so frontend types can be generated or kept aligned. Persistence should use Postgres/PostGIS for event storage and geospatial state, MapLibre should render the Taiwan map and overlays, OpenRouteService should provide avoid-polygon routing, and LLM usage should stay in controlled structured-output calls rather than a persistent agent swarm.
