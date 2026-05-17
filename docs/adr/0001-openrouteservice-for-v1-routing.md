# Use OpenRouteService for v1 routing

The v1 demo will use OpenRouteService to generate convoy route options from an origin, destination, and active denied-area polygons. This avoids building a custom road graph while still letting radio-derived hazards affect routing in a concrete geospatial workflow.

**Considered Options**

- Build a local road graph and routing engine.
- Compare only manually drawn route options.
- Use a routing service that accepts avoid polygons.

**Consequences**

The demo depends on OpenRouteService availability and API behavior, but keeps routing achievable while preserving the core product story: tactical radio reports become geospatial constraints that change logistics recommendations.
