# Constants

## A repeated literal becomes a named constant the moment a second call site needs it

A string or numeric literal that means something — an event type, a metadata key, a status value from a
third-party SDK, a policy name — is data with a name, not incidental syntax. The instant the same literal
is typed a second time, in a second file, extract it. Two identical literals a grep apart is not
"duplication that might matter later" — it is a spelling mistake in one of them waiting to happen, with no
compiler that will ever catch it.

Group related literals into one small `static class` named for the category they belong to, as a plural
noun (`TransactionTypes`, `PaymentMetadataKeys`, `RateLimitPolicies` — not `TransactionType`, singular,
which reads as one value rather than the vocabulary). Every call site references the constant, never the
literal it holds.

## Placement: the root of the project that owns the vocabulary, not a subfolder of its first caller

A constants class is part of a project's vocabulary — put it where a reader scanning that project's root
would expect to find "the fixed values this project works with," not buried inside the feature or mapper
folder of whichever file happened to need it first. Filing it under `Mappers/` or `Services/` ties a
project-wide vocabulary to one caller's implementation detail and makes the next consumer search for it
instead of finding it.

- **Visible to more than one project** (an event payload, a metadata key producers and consumers both read,
  any value that crosses a service or module boundary): lives in the owning `.Contracts` project, `public`,
  at that project's root.
- **Internal to one project** (a third-party SDK's own string vocabulary, a policy name only that service's
  host registers): lives at the root of the project that consumes it, `internal`, sealed off from anything
  outside that project's boundary.

Either way: the project root, not a subfolder — a constants class is discovered by browsing the project,
not by already knowing which file happens to reference it.

## One class per cohesive vocabulary — never one catch-all grab bag

`TransactionTypes` and `PaymentMetadataKeys` are two classes because they are two unrelated vocabularies
that happen to live in the same project, not one `Constants.cs` with every literal the project owns
sorted alphabetically. A grab-bag file answers "is there a constant for this?" only by reading the whole
thing; a class named for its vocabulary answers it from the class name alone. Splitting by vocabulary is
also what keeps a genuinely cross-service vocabulary (`Contracts`) separate from a genuinely internal one —
merging them into one file is how an internal-only value quietly leaks into a published contract.

## Do not reach for this when the literal already has a stronger home

A value that a shared `FrozenDictionary`/`FrozenSet` translation table (see the `csharp-naming` skill) maps
from already has its canonical form living as that table's keys — do not additionally mint a constants
class duplicating the same strings beside it. And a value whose *distinct outcomes* are really behaviour,
not data, is a keyed strategy (see the `keyed-strategies` skill), not a constant to switch on.
