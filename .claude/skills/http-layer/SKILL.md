---
name: http-layer
description: The client's HTTP layer — one `xApi` object per resource under the feature's `api/` folder, the response shape typed on the request generic, one HTTP-client instance per backend service created bare in the core package and enhanced with base URL, auth and tenant headers only in the app tree, and API errors resolved once at the query client's global handler with typed `meta` opt-outs, a shared retry policy, and the single legitimate exception of a route guard branching on status through the shared error seam rather than importing the HTTP library's own error helpers. Use when adding an api module or endpoint call, wiring auth or headers onto a client, writing a `try/catch` or `onError` around an API call, or adding a client for another backend.
---

# http-layer

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/http-layer/SKILL.md.
