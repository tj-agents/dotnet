---
name: event-dispatch
description: EF Core domain-event dispatch through SaveChanges interceptors, clearing collected events, transactional pre-commit work and the distinction between saving and committing an enclosing transaction. Use when implementing or reviewing event dispatch around EF Core SaveChanges, an outbox, or an explicit transaction.
kind: contract
domain: dotnet
profile: domain-model
applicability: EF Core projects dispatching domain events at the persistence boundary
requires: ef-core, domain-events
provenance: library, architecture, house
---

# EF Core event dispatch

```csharp
var transaction = await context.Database.BeginTransactionAsync(ct).ConfigureAwait(false);
await using (transaction.ConfigureAwait(false))
{
    await context.SaveChangesAsync(ct).ConfigureAwait(false);
    await transaction.CommitAsync(ct).ConfigureAwait(false);
}
```

The transaction owner starts with already-staged changes. `SavedChangesAsync` runs during the save,
while this explicit transaction is still uncommitted. The later `CommitAsync` is the commit boundary;
outbox rows staged by pre-commit handlers must enlist in that same transaction. No direct bus publish
is added after either call.

`dotnet:domain-events` owns event raising, handler contracts and translation to integration events.
This skill owns their EF Core persistence adapter. It selects no product-specific dispatcher or outbox.

Collect events from tracked raisers and clear their collections before dispatch: a nested save must not
redispatch the same events. Pre-commit handlers run before the owning transaction commits, and their
writes, including outbox rows, must enlist in that same transaction. An interceptor callback by itself
does not make writes in another context atomic; follow `efcore:persistence` for transaction ownership.

A `SavingChangesAsync` interceptor is a possible dispatch point when the adapter establishes that
transaction contract. It must preserve cancellation and both synchronous and asynchronous save behavior
supported by the application. Expected failures propagate to the transaction owner before classification.

`SavedChangesAsync` means the save completed. An explicit or ambient transaction may still be open;
therefore this callback is not a general after-commit signal. True after-commit effects belong to the
transaction owner or a committed outbox. Never publish outside the outbox and assume a completed save
makes delivery atomic.

[Microsoft transaction documentation](https://learn.microsoft.com/en-us/ef/core/saving/transactions)
distinguishes a save's implicit transaction from an explicit transaction spanning several saves.
[SaveChanges interception](https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/interceptors#savechanges-interception)
documents the save callbacks; commit ownership remains with the selected persistence implementation.

Tommy, 2026-10-18: EF Core-specific guidance has an `efcore` owner so generic domain events remain usable
without EF Core. This is an ownership split, not a replacement event infrastructure.
