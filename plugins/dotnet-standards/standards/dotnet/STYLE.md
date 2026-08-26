# C# style

Style rules an analyzer can express belong in `.editorconfig`, not here. Configure these at
`severity = error` and the prose below shrinks to the diagnostic ID:

| Rule | Setting |
|---|---|
| No underscore prefix on private instance fields | `dotnet_naming_rule` + a camelCase-only style |
| `this.` on field access | `dotnet_style_qualification_for_field = true:error` |
| No braces on a single statement | `csharp_prefer_braces = when_multiline:error` |
| File-scoped namespaces | `csharp_style_namespace_declarations = file_scoped:error` |
| Seal what isn't inherited from | `MA0053` |
| No inline logging | `CA1848` (see the `logging` skill) |

The rules below are the ones prose has to carry, plus the reasoning behind the enforced ones.

## Model value semantics and real choices

Use a `readonly record struct` for a small immutable value whose identity is entirely its fields when
`default(T)` is valid or harmless. Keep construction private when ordinary creation canonicalizes the
value, but remember that every struct still has an all-default value; reject that value at the consuming
invariant boundary when it is merely harmless. If an invalid default must be impossible to represent, use
a reference value object instead.

An enum represents a genuine closed choice. Do not introduce a one-member enum for possible future
variation, and do not encode an unrelated consumer's workflow vocabulary in a lower-level component.
When the component supports several modes, accept its own provider-neutral mode from the caller and
validate every defined choice.

## Private fields carry no underscore prefix; constructors qualify with `this.`

```csharp
// CORRECT
private readonly OrderDbContext context;

public OrderService(OrderDbContext context)
{
    this.context = context;
}

// WRONG
private readonly OrderDbContext _context;
```

**Every constructor assignment is `this.`-qualified — fields *and* public auto-properties.** Where a
member is a surfaced public auto-property, still write `this.Property = param`. Uniform `this.` makes
the member-vs-parameter split obvious at a glance instead of depending on the reader knowing which
identifiers are members.

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

## Captured state uses explicit `private readonly` fields, not primary-constructor captures

Anything a method or property reads must be an explicit `private readonly` field assigned via
`this.field = param`. This covers services, repositories, handlers, validators, and any base class
that reads its own dependencies.

A constructor that only forwards to `base(...)` and captures nothing may use a primary constructor —
there is no field to make `readonly`, so the shorthand is the clearest spelling. Pure base-forwarding
leaf types are the standing example.

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

## Call an inherited member through `base.`

```csharp
// CORRECT — CurrentScope is defined on the base, not here
return await base.CurrentScope.Where(x => x.IsActive).ToListAsync(ct);

// WRONG — reads like a local member
return await CurrentScope.Where(x => x.IsActive).ToListAsync(ct);
```

It tells the reader the member lives on the base so they don't hunt for a definition that isn't in
this file.

## `#region` only where a file aggregates many same-shaped members

Regions hide code and usually signal a class that should be split. They earn their place in exactly one
shape: a file that legitimately aggregates one member shape, where grouping by owner is the only
practical way to navigate — the canonical case being a project's `Log.cs`, partitioned into regions
named for the emitting class. Name a region for the thing it groups, never a generic label. If the type
is not an aggregator of one member shape, split it instead of regioning it.

Test classes have the analogous rule — region per method under test — in the `unit-testing` and
`integration-testing` skills.

## New extension members go in `extension()` blocks

All ordinary extension members use `extension(Receiver)` blocks — the C# 14 unified form, which also
covers properties, indexers, and static members and groups them by receiver. Keep receiver-owned members
in one `XExtensions` static class; an `XMappers` mapping family may hold one block per related receiver.
Do not add a new legacy `public static … (this X x)` method.

When you edit an existing extension container, migrate every ordinary member in it, so that no class ever
mixes `extension()` blocks with legacy `this` parameters. A container left untouched stays legacy until
its own sweep — track that as tech debt rather than half-migrating a class.

The one exception is a declaration contract that genuinely requires the receiver in the method signature.
A source-generated `[LoggerMessage]` partial method is declared
`internal static partial void PublishedOrderEvents(this ILogger logger, int count)` and stays in that
form; see the `logging` skill.
