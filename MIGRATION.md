# Canonical source migration

The pre-1.1 layout split each capability between a router under `.agents/skills` and a document under
`standards/dotnet`. Version 1.1 makes `.agents/<kind>/<name>/SKILL.md` the single authored definition and generates
all discovery and distribution copies. Public plugin and skill identities are unchanged.

The migration also classifies the four debug procedures as operations and records explicit selection profiles and
prerequisites. The stack-free core is comments, C# naming, and C# style. Existing repositories can keep loading the
same `dotnet:<skill>` identities; they should select optional guidance only where its declared prerequisite exists.
