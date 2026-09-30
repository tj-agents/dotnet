---
name: csharp-naming
description: Shared C# naming conventions — domain vocabulary, identifiers, interface/type pairing and readable method names. Routes domain modeling, value construction, collaborator responsibility, return contracts, validation, persistence, data shapes, mapping and transport naming to their owning standards. Use for shared identifier decisions or to locate the naming standard for the concern being changed.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: language, house
---

# Shared C# naming

## Applicability and ownership

These conventions apply to C# independently of an application stack. The table selects the additional
owner for the task at hand; load the relevant owner when its concern and prerequisites apply.

| Task | Naming owner |
|---|---|
| Design an entity, value object, aggregate or domain service when DDD is selected | [dotnet:ddd](../ddd/SKILL.md) |
| Choose an immutable value representation, construction or owned behavior | [dotnet:value-semantics](../value-semantics/SKILL.md) |
| Define a collaborator role, operation and semantic outcome | [dotnet:collaborator-naming](../collaborator-naming/SKILL.md) |
| Select application presence/failure carriers when Reunion is selected | [dotnet:result-carriers](../result-carriers/SKILL.md) |
| Name a data contract or query result | [dotnet:data-contract-naming](../data-contract-naming/SKILL.md) |
| Name a mapper or receiver extension | [dotnet:mapping](../mapping/SKILL.md) |
| Name a repository, persistence operation and storage return contract | [dotnet:repository-naming](../repository-naming/SKILL.md) |
| Implement EF Core repository/context conventions when selected | [dotnet:persistence](../persistence/SKILL.md) |
| Distinguish tenant visibility in repository contracts | [dotnet:multitenancy](../multitenancy/SKILL.md) |
| Name HTTP contracts or routes | [dotnet:http-api](../http-api/SKILL.md) |
| Name protobuf messages and RPC contracts | [dotnet:proto](../proto/SKILL.md) |
| Name projects and module folders | [dotnet:module-structure](../module-structure/SKILL.md) |
| Name domain events | [dotnet:domain-events](../domain-events/SKILL.md) |
| Name typed application errors | [dotnet:result-errors](../result-errors/SKILL.md) |
| Define validator names, methods and results when the validation profile is selected | [dotnet:validation](../validation/SKILL.md) |
| Name keyed strategy families | [dotnet:keyed-strategies](../keyed-strategies/SKILL.md) |
| Name unit tests | [dotnet:unit-testing](../unit-testing/SKILL.md) |

## Reuse the domain language and responsibility owner

Select the concern owner from the table before naming or moving a contract. A collaborator operation
loads its role owner and the selected return-contract owner; a data shape loads its own naming owner.
Each owner defines its concern once. Shared spelling conventions apply across them.

Read the declaration, implementation and callers together. Reuse the established word for the same
concept within its bounded context. A distinct name expresses a distinct meaning or contract. Keep an
operation with its cohesive owner; establish responsibility before selecting a name for a new type.

The role names in these house standards are canonical for projects selecting them. Microsoft guidance
supplies language/framework conventions; selected libraries supply their API contracts. Preserve that
provenance when explaining a name.

Naming describes the architecture selected by the project. A repository capability, transaction or DI
registration keeps the semantics of that architecture. Changes to the architecture are separate design
decisions with their own justification.

## Types use nouns; methods express their operation

Follow [Microsoft's type-naming guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-classes-structs-and-interfaces):
use noun phrases for types and verb phrases for methods. Interfaces use the `I` prefix. An ordinary
interface/implementation pair shares its subject and role: `IOrderRepository` / `OrderRepository`.

Capability interfaces name the capability, such as `IDisposable` or `IPausable`. Their implementations
name their own subject and responsibility, such as `HostPauser`. Qualify an implementation when callers
need to distinguish a real alternative.

Use PascalCase for type and public member names, camelCase for parameters and locals, and the `Async`
suffix for asynchronous operations. Field formatting and constructor qualification belong to
[dotnet:csharp-style](../csharp-style/SKILL.md). File names follow their top-level type; each top-level
request, result, status and execution shape has its own correspondingly named file.

## Read the name in context

Follow [Microsoft's general naming guidance](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/general-naming-conventions):
prefer readable, meaningful names. Read the identifier with its receiver, parameters and return type.
Include distinctions the caller needs, such as scope, locking, units or revision; use the surrounding
context for information it already supplies.

The collaborator or persistence owner defines the verb and its semantic outcome together. Qualify an
operation by a meaningful returned shape, such as `ResolveSnapshotAsync`, or by a distinguishing input
key, such as `GetByCustomerIdAsync`. Boolean questions use `Is`, `Has` or `Can`; validation operations
use their validator contract. A responsibility change carries its return contract and caller handling
with it. A shared implementation step may use `Core` when a wrapper gives that step a different contract.
