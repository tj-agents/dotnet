---
name: constants
description: Named-constant standard for .NET services — a repeated literal (event type, metadata key, third-party SDK status value, policy name) is extracted the moment a second call site needs it, grouped into a small plural-noun static class per cohesive vocabulary, placed at the root of the owning project rather than a mapper or feature subfolder, public in the owning `.Contracts` project when the value crosses a service boundary and internal to one project otherwise, never merged into one catch-all grab-bag file, and never duplicating a value that already has a stronger home in a frozen lookup table or a keyed strategy. Use when a literal is typed a second time, choosing where a constants class lives, splitting or merging constants classes, or reviewing a magic string.
---

# constants

The standard is `standards/dotnet/CONSTANTS.md` in `tomjseery/dotagents`, deployed to `~/.agents/standards/dotagents/dotnet/CONSTANTS.md`. Read it and follow it; this skill only routes to it.
