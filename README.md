# dotagents

Personal config for AI coding agents (Claude Code, Codex, etc.), synced across machines.

## Layout

Mirrors `%USERPROFILE%` — copy or symlink each piece into place at the matching path.

```
AGENTS.md                          -> ~/AGENTS.md
                                       Agent-agnostic global instructions.

.agents/skills/                    -> ~/.agents/skills/
                                       Canonical, agent-agnostic skills. Source of truth —
                                       edit here, not in ~/.claude/skills. Two kinds: the
                                       command skills invoked by name (commit-push, worktree,
                                       sync, …) and the load-on-demand engineering standards
                                       (csharp-*, result-*, typescript-*, testing, …), which
                                       fire when a task matches their description.

.agents/sync-claude-skill-stubs.ps1 -> ~/.agents/sync-claude-skill-stubs.ps1
                                       Regenerates ~/.claude/skills/*/SKILL.md as one-line
                                       stubs pointing back at the canonical skill. Claude
                                       Code only discovers skills under .claude/skills, so
                                       this bridges it to the shared .agents/skills source.
                                       Each stub mirrors the canonical `description`, which
                                       is what decides whether a skill loads at all.

.claude/CLAUDE.md                  -> ~/.claude/CLAUDE.md
                                       Claude Code specific global instructions.

.claude/settings.json              -> ~/.claude/settings.json
                                       Claude Code global settings (hooks, permissions, etc).

.claude/Get-LastClaudeConversation.ps1 -> ~/.claude/Get-LastClaudeConversation.ps1
.claude/Search-ClaudeHistory.ps1       -> ~/.claude/Search-ClaudeHistory.ps1
                                       PowerShell helpers for browsing local Claude Code
                                       session transcripts.
```

## The standards map

Two kinds of skill live in `.agents/skills/`: **command** skills you invoke by name, and **standards**
skills that fire when a task matches their description. The map below is the index for the standards half —
**look a topic up here before writing a rule down**, so it lands in the one file that owns it.

**Frontend (TypeScript/React)**

| Topic | Skill |
|---|---|
| Which library for which job, and what is deliberately not used | `stack-defaults` |
| `interface` vs `type`, casing against the wire, optional vs nullable, discriminated unions | `typescript-style` |
| Naming the client's half of a contract — domain-noun reads, `XRequest` writes | `contract-naming` |
| Feature slices, hooks orchestrate and components render, Effect traps, closed-key dispatch | `react-structure` |
| Queries, mutations, query keys, invalidation, buffer vs variables | `server-state` |
| Store privacy, facade hooks, derived values, the one imperative session | `client-state` |
| `xApi` modules, one client per backend, errors resolved once | `http-layer` |
| Forms — parse the buffer, map the parsed result | `write-boundary` |
| Sharing across apps — intersection, slots over role checks, composed identity | `tiered-shared-code` |

**Backend (C#/.NET)**

| Topic | Skill |
|---|---|
| Style, naming, comments and XML doc | `csharp-style`, `csharp-naming`, `comments` |
| DI and dependency-holders, logging, validation | `dependency-injection`, `logging`, `validation` |
| Result and Option carriers, typed errors, transport terminals | `result-carriers`, `result-errors`, `result-terminals` |
| Persistence, multitenancy, keyed strategies | `persistence`, `multitenancy`, `keyed-strategies` |
| Module layering, service boundaries, gRPC/proto, HTTP contracts | `module-structure`, `microservice-boundaries`, `proto`, `http-api` |
| Seeding, and the three test tiers | `seeding`, `unit-testing`, `integration-testing`, `e2e-scenarios` |

### Named gaps — create the folder, write the skill

These slots are deliberately empty rather than silently missing. Adding one is a new
`.agents/skills/<name>/SKILL.md` plus a stub sync; nothing else moves.

Frontend: `routing` (typed routes, search-param validation, guards, loader vs query) ·
`component-design` (props typing, composition over configuration, when to split) ·
`styling` (beyond the choice in `stack-defaults` — tokens, variant taxonomy, primitive ownership) ·
`loading-and-errors` (skeleton vs spinner, suspense and error boundaries, where pending renders) ·
`accessibility` · `formatting` (dates, money, numbers behind one module) ·
`realtime` (connection lifecycle, subscription in an Effect, payload naming) ·
`frontend-testing` (what to test at which level) · `performance` (memo policy, keys, code splitting) ·
`type-safety` (no `any`, `unknown` at boundaries, no non-null assertion, `satisfies`) ·
`cross-platform` (shared versus platform code, navigation versus router, secure storage).

Backend: `messaging` (outbox and inbox, idempotent handlers) · `configuration` (options binding, secrets) ·
`caching` · `observability` (tracing, metrics, health) · `authorization` · `background-jobs`.

## Setup on a new machine

1. Clone this repo somewhere, or clone it directly as `~/.agents-src` — whatever's convenient.
2. Copy `AGENTS.md`, `.agents/`, and `.claude/` into `%USERPROFILE%`, merging with anything
   already there.
3. From `~/.agents`, run the stub sync so Claude Code can see the skills:
   ```
   pwsh sync-claude-skill-stubs.ps1
   ```

## What's deliberately excluded

Session transcripts, `.credentials.json`/`auth.json`, telemetry, caches, and any repo-scoped
work skills (e.g. Infonetica's Azure DevOps-linked skills, which live junctioned inside work
repos, never here). See `.claude/CLAUDE.md` for the work-vs-personal skill split.
