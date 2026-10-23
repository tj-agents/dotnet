---
name: naming
description: Generic C# identifier naming — every field, parameter and local named for what it holds (`IUserService userService`), casing and affixes, nouns for types and verbs for methods, interface/implementation pairs, role nouns matching their verb, one subject word per concept, booleans and namespace-aware type names. Use when naming or reviewing any C# type, member, field, parameter or local.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# C# naming

Owns every naming rule that holds for a C# identifier whatever its concern. A concern's own vocabulary —
collaborator roles, data shapes, repository verbs, events, errors, tests, transports, projects — lives with
that concern's skill and loads through its route.

## Name every variable for what it holds

```csharp
private readonly IUserService userService;
```

A field, parameter or local holding a collaborator takes that collaborator's subject and role,
without the `I`. A value takes its meaning rather than its type: `recipientEmail`. Source:
[Microsoft, naming parameters](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/naming-parameters).
## Casing and affixes follow the ecosystem

Per [Microsoft's identifier names](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names):
PascalCase for types, namespaces, public members, methods, positional record parameters and every constant;
camelCase for parameters and locals. Interfaces take `I`, type parameters a descriptive `T` name (`TEntity`),
attributes `Attribute`, asynchronous methods `Async`, and a class bound through the
[options pattern](https://learn.microsoft.com/en-us/dotnet/core/extensions/options) `Options`. A non-flags enum
is singular, a flags enum plural. Spell words out except universally known abbreviations. A file is named for
its one top-level type. Private field spelling is the house `dotnet:fields` convention.

## Types are nouns, methods are verbs, and a role noun matches its verb

Use noun phrases for types and verb phrases for methods
([Microsoft](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-classes-structs-and-interfaces)).
An interface/implementation pair shares its subject and role: `IOrderRepository` / `OrderRepository`. A role
noun is the agent noun of the one operation it performs — `TaxCalculator.Calculate`,
`ConnectionFactory.Create`, `InvoiceRenderer.Render` — so the call reads as the subject doing its job.

Capability interfaces name the capability, such as `IDisposable` or `IPausable`; their implementations name
their own subject and responsibility, such as `HostPauser`. Qualify an implementation only when callers
distinguish a real alternative.

## One word per concept

Reuse the established word for the same concept within its bounded context, with its exact plurality, across
every sibling: `OrderResolver` beside `IOrderRepository`, never `OrdersResolver`. A distinct word expresses a
distinct meaning or contract. Read the declaration, implementation and callers together, and establish a new
type's responsibility before naming it. A rename never changes the architecture: a repository capability,
transaction or registration keeps its semantics.

## Use the containing namespace when naming a type

Read a proposed type name with its namespace and existing responsibility owner. Add a subject or qualifier
when it names a domain concept, responsibility, contract or real distinction. Do not add a module, layer,
product or default-scope prefix merely to repeat its containing namespace or make the simple name globally
unique. For example, `Billing.IntegrationTests.ApiFixture` is clear without `BillingApiFixture`;
`OrderRepository` still names the repository's subject and role.

Apply the same rule to fixtures, test types and names proposed in code or plan snippets. Preserve
framework-defined and published contract names, and keep qualifiers that distinguish actual strategies or
capabilities. When two otherwise appropriate simple names collide at a rare call site, qualify the reference
or use a local `using` alias there.

## Read the name in context

Follow [Microsoft's general naming guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/general-naming-conventions):
prefer readable, meaningful names. Read the identifier with its receiver, parameters and return type.
Include distinctions the caller needs, such as scope, locking, units or revision; use the surrounding context
for information it already supplies.

Qualify an operation by a meaningful returned shape, such as `GetSummaryAsync`, or by a distinguishing
input key, such as `GetByCustomerIdAsync`. Boolean members and questions use `Is`, `Has` or `Can`. A shared
implementation step may use `Core` when a wrapper gives that step a different contract.
