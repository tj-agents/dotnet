---
name: react-structure
description: How React code is organized — the feature slice (`types`/`api`/`hooks`/`components`/`pages`/`schemas` under one folder), hooks that orchestrate versus components that only render, the raw-hook/facade-hook split, what an Effect is actually for and the "you might not need an Effect" traps (event handlers for events, render-time computation for derived data, a query for server data), and dispatching on a closed key through one exhaustive table rather than a switch copy-pasted across components. Use when adding a feature folder, deciding whether logic belongs in a component or a hook, reaching for `useEffect`, or writing a second branch on the same discriminator or role.
---

# react-structure

The standard is `../../standards/react/STRUCTURE.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/react/STRUCTURE.md`. Read it and follow it; this skill only routes to it.
