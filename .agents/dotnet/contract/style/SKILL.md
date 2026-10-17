---
name: style
description: General C# style any codebase follows — enforceable rules live in `.editorconfig`, an enum is a genuine closed choice, a plain null check on a variable, `null!` rather than `string.Empty` for populated-later members, brace and empty-block shape, and when an optional parameter has stopped paying for itself. Use when writing or reviewing any C# type, adding a parameter to an existing signature, or deciding whether a style rule belongs in prose or in `.editorconfig`.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language
---

# C# style

Owns the general C# style rules every codebase shares; opinionated conventions have their own skills.

## Applicability

This contract applies to every C#/.NET repository and has no application-stack prerequisite.

Style rules an analyzer can express belong in the repository's `.editorconfig` at `severity = error`,
not in prose. `dotnet:scaffold` writes them for a new project; an existing repository's own
`.editorconfig` is authoritative. Field naming and qualification are `dotnet:fields`; logging's CA1848 is
`dotnet:logging`.

## Model value semantics and real choices

Modelling a small immutable value or multi-value result, with a reference record by default and a
`readonly record struct` only when justified, is the `domain-values` contract.

An enum represents a genuine closed choice. Do not introduce a one-member enum for possible future
variation, and do not encode an unrelated consumer's workflow vocabulary in a lower-level component.
When the component supports several modes, accept its own provider-neutral mode from the caller and
validate every defined choice.

## Test variables directly for null

Use `is null` or `is not null` when the expression is already a local variable or parameter. Do not
recapture that variable with `is { } value`; the second name obscures a plain null check. For a nullable
value type, use `.Value` inside the guarded branch.

Reserve a property-pattern capture for avoiding repetition of a full object/member expression.

```csharp
// CORRECT
if (tenantId is not null)
    Load(tenantId.Value);

// CORRECT — avoids repeating the member access
if (request.Context.ActiveTenantId is { } tenantId)
    Load(tenantId);

// WRONG — tenantId is already the complete name
if (tenantId is { } value)
    Load(value);
```

## A populated-later member defaults to `null!`, never `string.Empty`

A non-nullable `string` that something else fills in — a deserialization DTO, a persistence entity, a
config-bound options class, an interceptor-stamped column — defaults to `null!`. An empty-string
default masks a missing value as a present-but-blank one; `null!` says plainly that something else
assigns this before use.

Where an empty string is the genuine runtime value (a `??` fallback, a `GetValueOrDefault`, a log
fragment) `string.Empty` is correct. Never the `""` literal.

```csharp
// CORRECT — the deserializer populates it
public string DisplayName { get; init; } = null!;

// CORRECT — empty string is the real fallback
var kind = metadata.GetValueOrDefault("kind", string.Empty);

// WRONG — placeholder default pretending to be a value
public string DisplayName { get; init; } = string.Empty;
```

## Braces and empty blocks

```csharp
// CORRECT
if (cancelled)
    return;

// CORRECT — a deliberately empty block is compact
catch (OperationCanceledException) { }
```

## An optional parameter that callers must name-skip has stopped paying for itself

An optional parameter earns its place only when call sites pass it *positionally and naturally*. The
moment varying one argument forces a call site to name-skip past another, the signature grew and
nothing reads more clearly. Prefer, in order: vary the value inline at the one call site that needs it
(especially in tests — a self-contained Arrange beats threading a knob through a shared helper), or add
a small focused overload. Keep the optional only when several call sites pass it the ordinary way.

```csharp
// WRONG — the named argument exists only to skip couponCode
private Task<int> PlaceAsync(int cartId, string? couponCode = null, string buyer = "Test Buyer");
var id = await PlaceAsync(cartId, buyer: "Ada");

// CORRECT — the one caller that needs a distinct buyer does the call inline
await client.PostAsync($"/api/orders/{cartId}", new { buyer = "Ada" });
```
