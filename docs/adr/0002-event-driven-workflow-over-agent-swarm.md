# Use an event-driven workflow instead of a persistent agent swarm

The v1 demo will keep Quarterback as the user-facing agent identity and use specialist agentic steps only where language judgment or ambiguity handling is required. Deterministic work such as transcription calls, georeferencing, denied-area construction, routing, persistence, and map projection will be implemented as tools or services rather than persistent agents.

**Consequences**

This keeps the system debuggable and avoids over-agentifying the backend, while still supporting an agentic product experience through Quarterback, radio interpretation, and interpretation review.
