# dotagents

`dot` is **dotNET**. Personal config for AI coding agents (Claude Code, Codex, etc.), synced across
machines, plus the generic .NET engineering standards. The TypeScript/React half is
`tomjseery/react-agents`; anything Concertable-specific is `Concertable/agent-standards`.

**How this is authored and delivered — read [`ARCHITECTURE.md`](ARCHITECTURE.md) before changing the
shape of any of it.** It carries the repo map and why the repos stay separate, the
authoring → generate → install chain, the per-machine setup for both harnesses, and what a new project
needs (almost nothing).

## Layout

Mirrors `%USERPROFILE%` — copy or symlink each piece into place at the matching path.

```
AGENTS.md                          -> ~/AGENTS.md
                                       Agent-agnostic global instructions.

.agents/skills/                    -> ~/.agents/skills/ (utilities only)
                                       Skills, flat, because discovery is skills/*/SKILL.md and
                                       does not recurse. Source of truth — edit here. Two kinds:
                                       a STANDARD, which declares `domain:` and whose body IS
                                       the standard itself, and a UTILITY invoked by name
                                       (commit-push, worktree, sync, …) whose body is the
                                       procedure.

SKILLS.md                              Generated catalogue: skill -> what it covers -> owning
                                       plugin. Answers "did I write this rule down?" without
                                       opening anything.

.agents/sync-generated.ps1         -> ~/.agents/sync-generated.ps1
                                       Regenerates .claude/skills/*/SKILL.md, the plugin
                                       payloads and SKILLS.md. Claude Code only discovers skills
                                       under .claude/skills, so this bridges it to the shared
                                       .agents/skills source. Refuses to write when the skills
                                       and the plugin payloads disagree.

.agents/deploy-skills.ps1          -> ~/.agents/deploy-skills.ps1
                                       Junctions the UTILITY skills into ~/.agents and ~/.claude,
                                       so a `git pull` IS the deployment, and prunes the retired
                                       ~/.agents/standards tree. Standards are not junctioned:
                                       plugins deliver those, and the plugin namespace is what
                                       keeps two repos' same-named skills apart.

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

**The skill is the payload.** A standard is authored in exactly one file,
`.agents/skills/<name>/SKILL.md` — front matter declaring `domain: dotnet`, then the standard itself.
There is no separate doc: `@`-import expands only inside `CLAUDE.md`/`AGENTS.md`, never inside a
`SKILL.md`, so a skill naming a doc could only ever be a pointer that cost an extra Read for content the
invocation always needed.

**Look a topic up in [`SKILLS.md`](SKILLS.md) before writing a rule down**, so it lands in the one skill
that owns it. It is generated from the skill tree, so it cannot drift from it — which the
hand-maintained table its predecessor replaced could and did.

React/TS standards are not here — look them up in
[`react-agents`](https://github.com/tomjseery/react-agents). Process standards (branching, committing,
merging, plans) are not here either; they are Concertable-org and live in
`Concertable/agent-standards`.

**A generic standard and its Concertable counterpart share a skill name on purpose** — `persistence`
here and `persistence` in `agent-standards` — and the plugin namespace tells them apart:
`dotnet-standards:persistence` against `dotnet:persistence`. Install whichever pair a repo needs and
invoke the one you mean.

### Named gaps — create the node, write the standard

These slots are deliberately empty rather than silently missing. Adding one is a new skill; nothing else
moves.

`messaging` (outbox and inbox, idempotent handlers) · `configuration` (options binding, secrets) ·
`caching` · `observability` (tracing, metrics, health) · `authorization` · `background-jobs`.

The frontend gaps moved out with the corpus; they are listed in `react-agents`' README.

## Setup on a new machine

1. Clone this repo to `~/source/repos/dotagents`, and `tomjseery/react-agents` and
   `Concertable/agent-standards` beside it.
2. Copy `AGENTS.md` and `.claude/` into `%USERPROFILE%`, merging with anything already there.
3. Junction the utility skills into place:
   ```
   pwsh .agents/deploy-skills.ps1 -WhatIf   # inspect first
   pwsh .agents/deploy-skills.ps1
   ```
   Standards arrive from plugins, so install those first — see `ARCHITECTURE.md`. The script refuses to
   clobber a real directory it has no source for.

## What's deliberately excluded

Session transcripts, `.credentials.json`/`auth.json`, telemetry, caches, and any repo-scoped
work skills (e.g. Infonetica's Azure DevOps-linked skills, which live junctioned inside work
repos, never here). See `.claude/CLAUDE.md` for the work-vs-personal skill split.
