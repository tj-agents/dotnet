---
name: contract-naming
description: Naming the client's half of an HTTP contract — reads take the plain domain noun with no `Dto` or `Response` suffix (those are the server's words and differentiate nothing on the client), writes take `XRequest` carrying only client-settable fields with identity coming from the route, a suffix survives only where it distinguishes two real shapes, and every feature's reads and requests live in one `types.ts` the api module imports. Use when naming a type that mirrors a server payload, shaping a write body, deciding whether to keep a suffix, choosing where a contract type lives, or weighing generated clients against hand-written types.
---

# contract-naming

The standard is `standards/react/CONTRACTS.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/react/CONTRACTS.md`. Read it and follow it; this skill only routes to it.
