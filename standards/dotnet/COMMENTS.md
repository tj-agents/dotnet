# Comments and XML documentation

**The policy — default to zero comments, the *why* lives in the commit message — is always-applicable
and lives in your global agent instructions, not here.** This skill is only the C# mechanics that apply
once a comment has genuinely earned its place.

## Mechanics

A why-comment is one line where it can be, so `//`. The rare genuinely multi-line one is a single
`/* */` block, never stacked `//` lines.

Put the `//` on its own line directly above the statement, or inline after it with a single space. Never
pad with spaces to align comments into a column.

## A `<summary>` is for a member a reader would otherwise misuse

Use them **sparingly**. Add one only where a developer — or an agent — reading the code later would
genuinely benefit: real ambiguity, a non-obvious constraint, a safety or ordering subtlety, an API
contract. A summary that restates the member name earns its deletion.

**Never document both an interface and its implementation.** The contract lives on the interface; that is
the one place a summary belongs. The implementing class repeats nothing — leave it bare unless the
*implementation itself* has a quirk the interface cannot speak to (a specific algorithm, a workaround).
Two summaries saying the same thing is drift waiting to happen.

Where a type or member is documented, write an XML doc comment (`/// <summary>…</summary>`), not a `//`
line. Reserve `//` for short notes *inside* method bodies. Cross-reference with `<see cref="…"/>` and
`<see langword="null"/>` rather than bare prose, and use `<c>Name</c>` for a type the declaring assembly
cannot reference — that avoids an unresolved-cref warning.

**Lead with what the thing *is*, in plain words.** "A snapshot of the agreement, frozen at acceptance."
beats terse jargon about columns being copies rather than references. Name the kind-of-thing ("a snapshot
of X", "a cache of X", "a guard that…"), then add only the constraint that matters. A good "X of Y" opener
usually carries the whole summary on its own.

```csharp
// CORRECT — documents the member's non-obvious constraint
/// <summary>
/// The owning tenant. Settable so <c>TenantInterceptor</c> can stamp it at SaveChanges; domain
/// code never sets it directly.
/// </summary>
Guid TenantId { get; set; }

// WRONG — a docstring smuggled in as a line comment on a member
// Settable so the interceptor can stamp it
Guid TenantId { get; set; }
```
