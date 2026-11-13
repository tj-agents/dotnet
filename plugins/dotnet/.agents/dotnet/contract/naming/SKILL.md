---
name: naming
description: Generic C# identifier naming — every field, parameter and local named for what it holds (`IUserService userService`), casing and affixes, nouns for types and verbs for methods, interface/implementation pairs, the pattern words (`Factory`, `Builder`, `Provider`, `Accessor`, `Resolver`, `Registry`, `Policy`, `Context`, `Checker`), one subject word per concept, booleans and namespace-aware type names. Use when naming or reviewing any C# type, member, field, parameter or local.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# C# naming

Owns every naming rule that holds for a C# identifier whatever its concern. A concern's own vocabulary —
data shapes, persistence, validation, messaging, events, errors, tests, transports, projects — lives with
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
`ConnectionFactory.Create`, `InvoiceRenderer.Render`, `OrderExporter.Export` — so the call reads as the
subject doing its job. A type whose job takes two verbs to describe is two types. A one-operation type is
not a `Service`, which orchestrates a use case over repositories and owns its unit of work, and not a
`Factory`, whose `Create` builds a valid instance and guards its invariants: `OrderExporter`, never
`OrderExportService`.

Name a type for what it holds. A collective noun standing in for that — `Catalog`, `Model`, `Manager`,
`Helper`, `Data`, `Info` — is padding; a type whose members need different nouns is several types.

```text
OrderExporter.Export          not OrderExportService.Export or OrderExportFactory.Create
PermissionSet                 not PermissionCatalog, PermissionManager or PermissionHelper
```

Capability interfaces name the capability, such as `IDisposable` or `IPausable`; their implementations name
their own subject and responsibility, such as `HostPauser`. Qualify an implementation only when callers
distinguish a real alternative.

## Pattern words

| Word | Use when the class |
|---|---|
| `Factory` | Returns a new, ready instance from one call |
| `Builder` | Is configured across several calls, then produces its result once |
| `Provider` | Is one pluggable implementation supplying a value or capability, with no selection of its own |
| `Accessor` | Exposes a value another component stored |
| `Resolver` | Turns a reference — a name, key or type — into the thing it denotes by rules; finding nothing is a valid answer |
| `Registry` | Holds a keyed collection filled at startup and looked up by key |
| `Policy` | Is a side-effect-free rule a mechanism consults |
| `Context` | Holds the ambient state of the current request or operation for consumers to read, and does no I/O |
| `Checker` | Is injected to answer one boolean question, often by reading I/O, through an affirmative `Has…`, `Is…` or `Can…` method that returns `bool` and never throws |

A class that fits none takes the agent noun of what it does. Sources: .NET's `IHttpClientFactory`,
`WebApplicationBuilder`, `TimeProvider`, `IHttpContextAccessor`, `IJsonTypeInfoResolver`, `AuthorizationPolicy`,
`HttpContext`; Polly's `ResiliencePipelineRegistry`.

Keep a `Checker` distinct from its look-alikes: a `Guard` throws on a failed precondition; a `Validator`
returns field-keyed diagnostics for a boundary; a `Specification` is a pure in-memory predicate over a
candidate already in hand; a `Policy` or `Evaluator` returns a graded or structured result. Prefer a `bool`
method on the repository or read model that owns the data; a standalone `Checker` earns its place only when
it fans in across sources, needs a test seam or is swapped at the composition root.

## One word per concept

Reuse the established word for the same concept within its bounded context, with its exact plurality, across
every sibling: `OrderResolver` beside `IOrderRepository`. A distinct word expresses a
distinct meaning or contract. Read the declaration, implementation and callers together, and establish a new
type's responsibility before naming it. A rename never changes the architecture: a repository capability,
transaction or registration keeps its semantics.

## Use the containing namespace when naming a type

Read a proposed type name with its namespace and existing responsibility owner. Add a subject or qualifier
only when it names a domain concept, responsibility, contract or a real distinction from a sibling type,
never how a value was produced; the namespace already supplies module, layer and product. For example, `Billing.IntegrationTests.ApiFixture` is clear without `BillingApiFixture`;
`OrderRepository` still names the repository's subject and role.

Apply the same rule to fixtures, test types and names proposed in code or plan snippets. Preserve
framework-defined and published contract names, and keep qualifiers that distinguish actual strategies or
capabilities. A collision never chooses or rejects a name: when two otherwise appropriate simple names collide
at a rare call site, qualify the reference or use a local `using` alias there.

```text
PermissionSet, although System.Security.PermissionSet exists: alias the legacy type where both meet.
Not EffectivePermissions: "effective" says how the roles were merged, not what distinguishes the type.
```

## Read the name in context

Follow [Microsoft's general naming guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/general-naming-conventions):
prefer readable, meaningful names. Read the identifier with its receiver, parameters and return type.
Include distinctions the caller needs, such as scope, locking, units or revision; use the surrounding context
for information it already supplies. A name claims no more than its type holds: a lone hash is a `Hash`,
not a `Fingerprint`, `Revision`, `Record` or `Receipt`.

Qualify an operation by a meaningful returned shape, such as `GetSummaryAsync`, or by a distinguishing
input key, such as `GetByCustomerIdAsync`. Never restate a scope the caller or context already fixes:
`GetSummaryAsync`, not `GetOwnSummaryAsync`. Boolean members and questions use `Is`, `Has` or `Can`; `Try…`
is only the BCL shape, a `bool` with an `out` value, such as `TryGetMembership(tenantId, out var membership)`.
A shared implementation step may use `Core` when a wrapper gives that step a different contract.

A bare verb is self-describing only on a narrow type whose name already carries the subject:
`OrderExporter.Export`. On a broad surface, such as a module facade or a wide service, the method carries
the subject: `IOrderModule.ExportRecordsAsync`, not `IOrderModule.ExportAsync`.
