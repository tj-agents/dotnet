---
name: logging
description: Logging standard for .NET services — every message is a source-generated `[LoggerMessage]` method on the project's single `Log.cs`, never an inline `logger.LogInformation/LogWarning/LogError` template (`CA1848` at error severity makes the inline form fail the build), regions named for the emitting class, and the rule that a one-off debugging probe is also a `Log.cs` entry that gets deleted with the fix. Use when adding a log statement, adding observability to trace a hard bug, reviewing logging in a diff, or setting up a new project's `Log.cs`.
---

# logging

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/logging/SKILL.md.
