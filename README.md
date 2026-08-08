# dotagents

Personal config for AI coding agents (Claude Code, Codex, etc.), synced across machines.

## Layout

Mirrors `%USERPROFILE%` — copy or symlink each piece into place at the matching path.

```
AGENTS.md                          -> ~/AGENTS.md
                                       Agent-agnostic global instructions.

.agents/skills/                    -> ~/.agents/skills/
                                       Canonical, agent-agnostic skills. Source of truth —
                                       edit here, not in ~/.claude/skills.

.agents/sync-claude-skill-stubs.ps1 -> ~/.agents/sync-claude-skill-stubs.ps1
                                       Regenerates ~/.claude/skills/*/SKILL.md as one-line
                                       stubs pointing back at the canonical skill. Claude
                                       Code only discovers skills under .claude/skills, so
                                       this bridges it to the shared .agents/skills source.

.claude/CLAUDE.md                  -> ~/.claude/CLAUDE.md
                                       Claude Code specific global instructions.

.claude/settings.json              -> ~/.claude/settings.json
                                       Claude Code global settings (hooks, permissions, etc).

.claude/Get-LastClaudeConversation.ps1 -> ~/.claude/Get-LastClaudeConversation.ps1
.claude/Search-ClaudeHistory.ps1       -> ~/.claude/Search-ClaudeHistory.ps1
                                       PowerShell helpers for browsing local Claude Code
                                       session transcripts.
```

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
