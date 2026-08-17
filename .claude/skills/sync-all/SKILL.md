---
name: sync-all
description: Bring EVERY git worktree up to date with the default branch in one pass — the bulk counterpart to `sync` (which only updates the main checkout). Fetches once, then for each worktree merges `origin/main` into its branch (or `pull --ff-only` when it IS the default branch), auto-stashing and restoring any working changes, and aborting cleanly on any conflict so no tree is ever left half-merged. Use when Tommy says "sync all", "/sync-all", "sync all worktrees", "bring every worktree up to date", "get all my worktrees current with main", or after a merge that everything else should rebase onto.
---

# sync-all

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/sync-all/SKILL.md.
