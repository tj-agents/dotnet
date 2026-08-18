---
name: server-state
description: Server state belongs to the query library — every read is a query and every write a mutation, never a `useEffect` plus `useState` that hand-rolls caching, dedup, retries and error routing (including for a one-shot fire-on-mount action), query keys as arrays ordered generic to specific behind a per-feature factory so keys and invalidations cannot drift, and the split between a component's live input buffer and the mutation's variables, with everything constant for the hook's lifetime bound inside the hook. Use when loading or sending server data, reviewing a `useEffect` that fetches, designing query keys, wiring invalidation, or deciding what a mutation call should receive.
---

# server-state

The standard is `../../standards/react/SERVER_STATE.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
