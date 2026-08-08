---
name: pull-main
description: Sync the current repo's local main with origin without losing work — stash any working changes, switch to main, fetch + pull --ff-only, then restore the stash. Skips the stash/restore entirely when the tree is clean. Use when Tommy says "pull main", "sync main", "/pull-main", or wants local main brought up to date while keeping current changes.
---

# pull-main

Bring local `main` up to date with `origin/main`, carrying any current working changes back afterward. Run everything via the available shell/terminal tool from the repo root. No preamble — just do it and report the final state.

## Behavior

1. If the working tree is dirty, stash it (tracked + untracked, ignoring `.gitignore`d files). If it's clean, **skip** stashing and **skip** the later pop.
2. Switch to the default branch (`main`).
3. `git fetch`, then `git pull --ff-only`.
4. If (and only if) you stashed in step 1, `git stash pop` to restore the changes.

## Run this

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'); MAIN=${MAIN:-main}
STASHED=0
if [ -n "$(git status --porcelain)" ]; then
  git stash push -u -m "pull-main autostash" && STASHED=1
fi
git switch "$MAIN" 2>/dev/null || git switch -c "$MAIN" "origin/$MAIN"
git fetch origin
git pull --ff-only
if [ "$STASHED" = 1 ]; then
  git stash pop || echo "POP CONFLICT: your changes are safe as the most recent entry in 'git stash list' — resolve manually."
fi
echo "=== on $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD) ==="
git status --short
```

## Rules

- **Only pop the stash this skill created** — it's the newest entry, made seconds earlier. Never blind-pop when you didn't stash; the repo may hold unrelated stashes.
- **Never discard work.** If `pull --ff-only` fails (local main diverged) or the pop conflicts, stop and report — do not force, reset, or merge over it.
- Report the final branch, short HEAD sha, and whether changes were restored.
