---
name: fields
description: The house convention for how a C# type spells, declares and reaches its own state — private fields without an underscore prefix, `this.` only where a constructor parameter shadows the member it fills, explicit `private readonly` fields instead of primary-constructor captures, and `base.`-qualified inherited calls. Use when declaring a field, writing a constructor, choosing between a primary constructor and explicit fields, or calling an inherited member.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: house
---

# Fields and member qualification

Owns how a type spells, declares and qualifies its own state and inherited members. What a field is
called is `dotnet:naming`'s; this skill owns only its spelling.

## Applicability

This contract has no application-stack prerequisite. It is house: Microsoft's default spells private
fields `_camelCase`, `s_camelCase` and `t_camelCase`, so a codebase following that default replaces this
skill and keeps `dotnet:naming`. The repository's `.editorconfig` carries the enforceable half — the
private-field `camel_case` naming rule with `dotnet_diagnostic.IDE1006.severity = error`, and
`dotnet_style_qualification_for_field = false:error` — and `dotnet:scaffold` writes both.

## Private fields carry no underscore prefix; `this.` disambiguates a shadowed constructor parameter

```csharp
// CORRECT — "context" shadows the field, so this. disambiguates it
private readonly OrderDbContext context;

public OrderService(OrderDbContext context)
{
    this.context = context;
}

// WRONG
private readonly OrderDbContext _context;
```

A constructor with no same-named parameter has nothing to disambiguate, so the assignment stays
unqualified:

```csharp
// CORRECT — no parameter shares the field's name, so there is nothing to disambiguate
private readonly Inventory inventory;

public InventoryTests()
{
    inventory = new Inventory(new StockCatalog());
}
```

`this.` appears only where a constructor parameter is named after the member it fills and would otherwise
shadow it: there, `context = context;` is the self-assignment bug `this.` prevents. A constructor that builds
a field with no same-named parameter, or assigns a differently-named parameter to a public auto-property
(`Reserve = reserveStockStep;`), has nothing to disambiguate, so the assignment stays unqualified. The build
does not report a stray `this.` (IDE0003 is not a build diagnostic), so review catches it.

## Captured state uses explicit `private readonly` fields, not primary-constructor captures

Anything a method or property reads must be an explicit `private readonly` field assigned via
`this.field = param`. This covers services, repositories, handlers, validators, and any base class
that reads its own dependencies.

A constructor that only forwards to `base(...)` and captures nothing may use a primary constructor —
there is no field to make `readonly`, so the shorthand is the clearest spelling. Pure base-forwarding
leaf types are the standing example.

## Call an inherited member through `base.`

```csharp
// CORRECT — CurrentScope is defined on the base, not here
return await base.CurrentScope.Where(x => x.IsActive).ToListAsync(ct).ConfigureAwait(false);

// WRONG — reads like a local member
return await CurrentScope.Where(x => x.IsActive).ToListAsync(ct).ConfigureAwait(false);
```

It tells the reader the member lives on the base so they don't hunt for a definition that isn't in
this file.
