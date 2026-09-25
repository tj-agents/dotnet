# Global instructions (Tommy)

## Work vs personal repos — the Azure-DevOps / PR skills are WORK-ONLY

The skills **`create-devops-item`**, **`create-gh-pr`**, **`ship`**, and **`implement`** are
Infonetica **work** tools: they create Azure DevOps work items in the ERM project / CRIS Team,
link `AB#` items, set assignees, and open PRs wired to all of that.

They are physically scoped to work repos: they live in
`C:\Users\TommySeery\source\repos\infonetica\.claude\skills` and reach each work repo via an NTFS
junction at `<repo>\.claude\skills` (per-skill junctions in `cris-preaward-app`, which has its own
project skills). They are NOT in `~/.claude/skills`, so they simply don't exist in personal
projects. When adding a work repo, junction its `.claude\skills` to the shared folder and add the
path to `.git/info/exclude`.

In a personal repo (e.g. `Concertable`, or anything under `C:\Users\TommySeery\source\repos` that
isn't under `infonetica\`):

- Open PRs with **plain `gh pr create`** (GitHub only) — no work item, no `AB#`, no assignee.
- Commit / push with plain `git` or the generic `commit` / `push` skills.

## Don't park finished work or invent PR/branch strategy — commit it and push it on the CURRENT branch

Default for any change: apply it to the branch/PR **already in context**, commit it, and **push it there**.
Two failure modes that have wasted real time — never do either:

1. **Spinning up a new branch/PR for a change.** A separate branch or `gh pr create` is **opt-in only** —
   I ask for it explicitly. "fix this" / "fix this rq" / "dump it in" always means *on the current PR*.
   When unsure which PR is "this one," ask in one line — never guess by creating a new one.
2. **Parking finished, building work instead of pushing it.** Do NOT invent "keep this PR minimal",
   "refactor on a separate PR", "stacked branch", or "do it in a fresh session" plans, and never
   un-commit / reset / reshuffle git history to fit such a plan — those are MINE to request, never your
   default. If code is written and builds, it goes on the current branch and gets pushed. Finished work
   sitting unpushed "for a cleaner PR" is the bug — it's what made me keep asking "why isn't it pushed?".
   If you genuinely think a split is warranted, say so in **one line** and keep going on the current
   branch unless I say otherwise.

## Committing and pushing are free in personal repos (work repos tighten it — they gate both)

**`git commit`** — fine by default; it's a local, reversible checkpoint, not a publish. Commit at
natural boundaries (a completed change, a finished plan phase) **without asking** — "should I commit?"
is not a question to raise, and never leave completed, verified work sitting uncommitted "for review"
(the review runs on the commit; `/code-review` diffs committed history).

**Local (working-tree) edits** — reversible, so **make them, don't ask whether to.** Editing /
writing / refactoring, applying a fix, executing a plan's code steps is the *default action*, never a
"should I?" question and never a "just report / do nothing" option in a menu.

**Work repos override this — stricter.** Infonetica repos (under `source\repos\infonetica\`) require
Tommy's explicit go-ahead before **committing too**, not just pushing — see `infonetica\CLAUDE.md`.
The commit-freely default above is for personal projects (Concertable, Vel, cpp, …).

## Don't fuss about the commit-state of docs — "pushed" means the CODE

When Tommy asks "is everything pushed / committed / merged", he means the **actual code** — answer
that, directly and in one line ("yes, code's pushed"). Do **NOT** volunteer warnings about uncommitted
markdown/plans/docs, an untracked review file, a deleted lock file, or any other commit-state trivia:
working docs are fine sitting uncommitted and just ride the next PR/commit — he does not care, and
saying so unprompted (especially at length) is noise. No hand-waving, no hedging, no "but note that…"
about docs. If he wants a doc committed he'll say so. Answer the code question and move on.

## Code comments — default to ZERO (global, absolute, overrides any weaker project rule)

Applies in **every** repo, personal and work, in every language. This keeps getting violated — it
stops now.

**Default to no comment.** Well-named identifiers already say what the code does; the diff shows what
changed. A comment is a rare exception that must carry a *why* a reader needs **at that exact line**
and cannot get from the code itself — a footgun/invariant ("don't reorder — X must run before Y"), a
genuine upstream-bug workaround, a non-obvious legacy constraint. Nothing else earns one.

**Never write the design-narration comment** — the single worst offender, and the one that appears
most when redoing work or addressing review/PR feedback: the comment that explains the choice just
made or contrasts it with the alternative. "Mirrors the backend DTO", "served here, absent there",
"we do X not Y", "using A instead of B because…", "this replaces the old…". That is over-explaining.
The reasoning behind a change belongs in the **commit message**, never bolted onto the code as running
commentary. Redoing or re-editing something is not a licence to annotate it — that's exactly when the
urge is strongest and most wrong.

If a comment restates the identifier, narrates the *what*, or justifies a decision → delete it, and
put the *why* in the commit message if it matters. When in doubt, no comment.

## Never claim absence off an indirect search (all repos)

A grep, name scan or metadata dump locates candidates; it never proves "X doesn't exist". Before any
negative claim: enumerate the whole search space, check the method can even see the target (a name
scan can't see values or content inside instances), and confirm against the real thing. Say what was
verified vs only scanned.

## Topic playbooks: own doc, lazy pointer

Big tool/domain guidance goes in its own local `<TOPIC>.md` with a one-line "read before doing X"
pointer. Never `@`-included — most prompts don't need it.

## Review comments / messages I draft for Tommy to paste

Plain prose, no `>` blockquote and no wrapping code fence. Point + one option, then stop — no tail
justifying it or saying what it buys. Inline backticks on identifiers are fine.

## Editing files that load every prompt (AGENTS.md / CLAUDE.md / command + skill docs) — minimum words

Every word is a recurring per-prompt token cost. Fix existing wording in place as the first choice — never stack a new section on top of it. Add the fewest words that carry the rule — no examples, code blocks, or restating.
