# Architecture

dotagents owns generic .NET contracts only. Its terminal marketplace identity is dotagents and its sole
plugin identity is dotnet.

Authored sources:

- .agents/skills contains contract routers.
- standards/dotnet contains the contract documents.
- .agents/plugins contains marketplace and payload declarations.

Generated delivery:

- .claude/skills mirrors the canonical routers for repository-local Claude sessions.
- plugins/dotnet contains installable Claude and Codex manifests, routers, and standards.
- .claude-plugin/marketplace.json and .agents/plugins/marketplace.json describe the same plugin to their
  respective harnesses.

Concertable/agents owns Concertable-specific contracts, workflows, profiles, and hooks. base-agents owns
machine operations. react-agents owns generic React and TypeScript contracts. Shared behavior is never
copied between those repositories.
