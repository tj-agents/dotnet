---
name: result-errors
description: Typed application errors for .NET services — one closed, operation-owned `XError` union per operation implementing `IError`, declared with Dunet and implicit conversions disabled, placed beside its widest in-process caller, with `Definition` derived in a single exhaustive switch over `ErrorDefinition.Invalid/NotFound/Conflict/Unauthenticated/Forbidden/PaymentRequired/Validation` factories, published dot-separated codes derived from the owner and case names, `[ErrorCode]` only to preserve an already-published code, honest agreement between a case name and its semantic kind, and an exact definition contract test per case. Use when adding or changing an error case, designing an operation's failure set, choosing a semantic kind, renaming an error, or reviewing a shared error catalog or a `NotFound<T>` base class.
---

# result-errors

The standard is `../../standards/dotnet/results/ERRORS.md`, shipped in this plugin. Read it and follow it; this skill only routes to it.
