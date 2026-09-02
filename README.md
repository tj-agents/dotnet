# dotagents

`dot` is **dotNET**. Personal config for AI coding agents (Claude Code, Codex, etc.), synced across
machines, plus the generic .NET engineering standards. The TypeScript/React half is
`tomjseery/react-agents`; the stack-agnostic method — branching, plans, reviews, merging, and the hooks
that enforce them — is `tomjseery/process-agents`; anything Concertable-specific is
`Concertable/agent-standards`.

**How this is authored and delivered — read [`ARCHITECTURE.md`](ARCHITECTURE.md) before changing the
shape of any of it.** It carries the repo map and why the repos stay separate, the
authoring → generate → install chain, the per-machine setup for both harnesses, and what a new project
needs (almost nothing).

## Layout

Mirrors `%USERPROFILE%` — copy or symlink each piece into place at the matching path.

```
AGENTS.md                          -> ~/AGENTS.md
                                       Agent-agnostic global instructions.

standards/<domain>/                -> ~/.agents/standards/<domain>/
                                       The engineering standards themselves, as plain markdown
                                       organized by domain (dotnet).
                                       Source of truth — edit here. Each domain carries a
                                       generated INDEX.md answering "did I document this?".

.agents/skills/                    -> ~/.agents/skills/
                                       Skills, flat, because discovery is skills/*/SKILL.md and
                                       does not recurse. Two kinds: a UTILITY invoked by name
                                       (commit-push, worktree, sync, …) whose body is the
                                       procedure, and a ROUTER for a standard, which is front
                                       matter plus the path of the one doc it owns.

.agents/sync-generated.ps1         -> ~/.agents/sync-generated.ps1
                                       Regenerates .claude/skills/*/SKILL.md and every
                                       INDEX.md. Claude Code only discovers skills under
                                       .claude/skills, so this bridges it to the shared
                                       .agents/skills source. Refuses to write when a router
                                       and the tree disagree.

.agents/deploy-skills.ps1          -> ~/.agents/deploy-skills.ps1
                                       Junctions every skill and every standards domain into
                                       ~/.agents and ~/.claude, so a `git pull` IS the
                                       deployment. Skills and domains share one namespace
                                       across repos, so a duplicate name is refused.

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

**The doc is the payload and the skill is a router.** A standard is a plain markdown file under
`standards/<domain>/`, and its skill is eight lines naming that file. That buys a doc a second delivery
mode it could never have while the text lived inside a `SKILL.md`: a repo can `@`-import it to make it
always-on, or route to it by skill everywhere else.

**Look a topic up in its domain's `INDEX.md` before writing a rule down**, so it lands in the one file
that owns it:

| Domain | Index | Covers |
|---|---|---|
| `dotnet` | [`standards/dotnet/INDEX.md`](standards/dotnet/INDEX.md) | style, naming, comments, DI, logging, validation, `data/`, `results/`, `structure/`, `testing/` |

React/TS standards are not here — look them up in
[`react-agents`](https://github.com/tomjseery/react-agents).

Each index is generated from the tree, so it cannot drift from it — which the hand-maintained table it
replaced could and did. Process standards (branching, committing, merging, plans) are not here; they bind
to no stack and live in [`process-agents`](https://github.com/tomjseery/process-agents), which is also
where the write-time hooks ship from.

Doc names never repeat their folder (`dotnet/STYLE.md`, not `dotnet/CSHARP_STYLE.md`) while skill names
stay globally unique (`csharp-style`), because the deployed skill namespace is flat and spans every
stack.

### Named gaps — create the node, write the standard

These slots are deliberately empty rather than silently missing. Adding one is a new doc in the tree plus
its router; nothing else moves.

`messaging` (outbox and inbox, idempotent handlers) · `configuration` (options binding, secrets) ·
`caching` · `observability` (tracing, metrics, health) · `authorization` · `background-jobs`.

The frontend gaps moved out with the corpus; they are listed in `react-agents`' README.

## Setup on a new machine

1. Clone this repo to `~/source/repos/dotagents`, and `tomjseery/react-agents`,
   `tomjseery/process-agents` and `Concertable/agent-standards` beside it.
2. Copy `AGENTS.md` and `.claude/` into `%USERPROFILE%`, merging with anything already there.
3. Junction the skills and the standards trees into place:
   ```
   pwsh .agents/deploy-skills.ps1 -WhatIf   # inspect first
   pwsh .agents/deploy-skills.ps1
   ```
   A skill is a router, so deploying skills without their trees leaves every standard pointing at a file
   the session cannot open. The script does both, and refuses to clobber a real directory it has no
   source for.

## What's deliberately excluded

Session transcripts, `.credentials.json`/`auth.json`, telemetry, caches, and any repo-scoped
work skills (e.g. Infonetica's Azure DevOps-linked skills, which live junctioned inside work
repos, never here). See `.claude/CLAUDE.md` for the work-vs-personal skill split.
