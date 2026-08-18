# Explaining code

Applies to every explanation of behaviour: a PR, a bug, a design, a piece of a system. Not to short
factual replies ("yes, it's pushed").

Language-agnostic. C#, TypeScript, React, bicep, terraform, SQL, YAML, shell, Python — same rules.

## The rule: show the code, then explain it

Every claim about behaviour is anchored to lines that are on screen. An explanation that describes
code without showing it is unreviewable, because the reader has to reconstruct the file from prose
and hope the reconstruction matches.

**Paste the snippet first, explain underneath.** Not the reverse, and not "explain, then offer to
show it".

**Every message, not just the first.** A recap, a summary, a shortened re-answer, a list of findings
— each one re-pastes its snippets. "I showed it earlier" is not an exemption. A findings list written
as prose bullets is where this gets dropped, every time.

**A finding shows the edit it implies**, as the changed lines. "X is wrong" with no fix on screen is
a worry, not a finding. Where the fix isn't a code change, or there isn't one, say so outright.

## Never name a thing that isn't visible

"Step 2 also validates" when nothing was numbered and no code was shown is the failure this rule
exists for. "The second call", "the guard", "the early return", "the wrapper", "that overload" — all
meaningless until the reader can see the thing being named.

- Invent no shorthand. If numbering helps, number the snippets that are already pasted.
- Name a file and line for every snippet, `path/to/File.cs:180-185`, so it's clickable.
- Introduce no term without the code that defines it in view.

## Show the exact code

Snippets are verbatim. Elide with `...` where the detail isn't needed, but don't rewrite, re-order or
collapse lines, and don't let a cut make the code look like something it isn't.

Pull it with a real read of the real ref and say which one — `git show origin/main:path`,
`git show <branch>:path`, or Read. Line numbers come from that read, never typed by hand.

**Never paste minified, bundled or generated code.** A `dist` one-liner with single-letter names is
unreadable, so it proves nothing to the reader. Quote the readable source, or state the behaviour in a
sentence and prove it by running it and showing the output.

## Gloss the jargon

Any term, syntax or convention that isn't self-evident gets a one-line explanation the first time it
appears. Cron fields and `${{ }}` substitution in YAML; `useRef` vs `useState`, a discriminated union
or a generic constraint in TS; `IAsyncEnumerable`, a source generator, covariance in C#; a partition
key in Cosmos; `for_each` in terraform. A sentence inline, not a tutorial and not a glossary at the
end.

"What does this mean" always includes the terminology in it. Don't assume the jargon is the known
part and the logic is the question.

## Before/after means both

Any claim that a change alters behaviour shows the old lines and the new lines. One side alone is an
assertion. Same for "this used to work differently" — show the previous version from git history.

## Evidence is the real output, not a summary of it

Claiming something failed, passed, is slow, or returns a given value means showing the actual thing:
the test output, the stack trace, the log line, the query plan, the timing, the response body.
"The validate step passed and the deploy failed" is a claim. This is evidence:

```
6  success  Run preflight validation
7  failure  Deploy Bicep Template
```

## Keep the prose between snippets short

The snippets carry the explanation. Prose links them and says what to notice. Long paragraphs between
code blocks mean the code isn't doing the work.

## Assume nothing is already in the reader's head

Not the diff, not a file read three messages ago, not a term used earlier in the conversation. If the
answer depends on it, show it again.

The mechanism a change touches is context too. Explain what the thing is and what it's for before
saying whether the change is right, otherwise the verdict has to be taken on trust. The reader is
checking the reasoning, not accepting the conclusion, so a point they can't independently judge isn't
finished — but a point they can't *follow* isn't finished either. Cut every snippet, aside and
qualifier that wouldn't change the conclusion; volume the reader gives up on verifies nothing.
