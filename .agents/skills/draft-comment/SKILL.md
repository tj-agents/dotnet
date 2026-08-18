---
name: draft-comment
description: Draft a PR review comment, a reply to a reviewer, or a Teams/Slack message that Tommy posts himself. Use whenever the output is text he pastes under his own name, including every finding a code review produces. Each point ships as two layers — the short comment he pastes, then the analysis underneath that lets him verify it instead of trusting it. Covers his wording conventions: point then one option then stop, prefer a question, no em dashes, no blunt imperatives, plain prose with no blockquote or wrapping fence.
---

# draft-comment

Every point ships as **two layers with opposite rules**, in this order: the comment, then the analysis
under it. Blending them is the failure this skill exists to stop — a bloated comment, or a finding too
thin for him to defend when the author pushes back.

**Never ship one layer alone.** A comment with no analysis is something he has to take on trust, and
he will ask what it means. An analysis with no comment is a review write-up, not a draft.

## Layer 1 — the comment, for the author

He is the one posting it. Fill the gap and stop.

**Say where it goes.** Prefix every comment with the `file:line` it attaches to, as a label above the
text, never inside it, so he can find the spot in the diff without hunting.

**Name every location the comment mentions.** The label covers the anchor line only. Any *other* code
the comment refers to carries its own `file:line` inline, and the snippet under the sentence whenever
the point turns on what those lines say. "over in OrganisationsService" is unreadable on its own;
`OrganisationsService.cs:169` plus the one line it names is not. A comment must stand alone without the
analysis under it, because the author only ever sees the comment.

**Shape.** Point, then one option, then stop. No preamble, no menu of alternatives, no closing
sentence justifying the point or saying what it buys, no "want me to post it?".

**Prefer a question over a directive** when the author might know something you don't. It lets them
answer "no, because X" without it being a fight, and it doesn't spell out a consequence they can work
out for themselves.

**Voice.**
- **No em dashes.** Commas, full stops, or "so"/"though".
- **No blunt imperatives.** Not "drop it", "cut this", "delete". Prefer "I don't think we need this",
  "probably don't need it", "feels redundant", "worth keeping X though".
- Casual and conversational, not clipped or robotic.
- **Don't over-explain the why.** He reviews seniors. State the point, show the code, skip the
  paragraph justifying it.
- **Don't tally a repeated problem at the author** ("this is the fourth one I've seen", "you keep
  doing this"). Keep it neutral about the pattern: "I've seen a lot of these around the codebase,
  they're all basically the same, so we should pull it into a shared component."

**Formatting.** Plain prose. No `>` blockquote, no wrapping code fence. Inline backticks on
identifiers are fine, and a fenced snippet under the sentence is fine when the point is a code change.

**Compliment-then-nudge** is his preferred shape when something is done well but could go further.
Acknowledge, then nudge, no filler:

    Good using keyof rather than string. Same could apply to value so it's typed per key instead of
    just string:

followed by the snippet.

### Worked example

The finding: a path filter greps `^infrastructure/`, but `dbThroughput` and friends are inputs in
`ci.yml`, so changing one silently skips provisioning.

Too long, prescribes the fix, spells out the consequence:

    The filter only looks at `infrastructure/`, but the sku, instance count and dbThroughput are
    inputs here in ci.yml, so changing one of those wouldn't trigger a provision and it'd sit
    unapplied until the Monday run. Worth widening the pattern to cover ci.yml and bicep-deploy.yml
    too.

His version:

    the filter only looks in infrastructure, but what about changes in ci.yml? would that also
    require a bicep rerun?

Shorter, a genuine question, no prescribed fix, no consequence spelled out.

## Layer 2 — the analysis, under the comment

**Invoke the `explaining-code` skill and follow it.** Snippet first with `file:line`, explanation
underneath. Before **and** after whenever the claim is that a change altered behaviour. Gloss the
jargon. Show the edit the comment implies as changed lines, or say outright there isn't one.

Thorough is correct here — the opposite of Layer 1. He is checking the reasoning, not accepting the
conclusion, so a point he cannot independently judge isn't finished.

**Say how he can check it himself** where the claim rests on runtime or stored state rather than on
the lines alone: which page, which record, which query, which log.

**A point whose analysis you cannot write is not a finding.** Drop it rather than posting a worry.

## Line numbers come from the branch under review

The local checkout is usually a different branch, and it is never the source.

```
gh pr view <pr> --json headRefName
git fetch origin <head-branch>
git show origin/<head-branch>:<path>
```

Numbers come from that read, never from memory or from a diff hunk header. A `#` in a branch name
needs quoting in the shell.

## Ordering and scope

Most severe first. Say which points you would not post at all, rather than padding the list.

## Never post it yourself

No PR comments, no replies on review threads, no resolving. He posts, the reviewer resolves.
