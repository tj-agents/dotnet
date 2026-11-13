---
name: dtos
description: The words for C# data shapes — the plain noun (or `XEntity`), `XSummary` for a list row, `XDto` where it would clash with a same-named entity, and `Pagination<T>` (or `IPagination<T>`) for one page. Use when naming or reviewing a record, DTO, query result or other shape carried between callers.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: house
---

# DTO naming

Owns the words for data shapes carried between callers. A shape that fits none of these takes the plain domain
noun.

```csharp
public sealed record VenueSummary(Guid Id, string Name);

public sealed record VenueDto(Guid Id, string Name, string City);

public sealed record Pagination<T>(IReadOnlyList<T> Items, int TotalCount, int PageNumber, int PageSize);
```

| Word | Use when |
|---|---|
| `Venue` (or `VenueEntity`) | The shape is the thing itself; `VenueEntity` where the codebase already suffixes its entities |
| `VenueSummary` | The reduced row of a list |
| `VenueDto` | The application shape would otherwise clash with the same-named entity or domain type |
| `Pagination<T>` (or `IPagination<T>`) | One page of a list |

Repository projections belong to `dotnet:repositories`; HTTP and gRPC bodies to `dotnet:http-api` and
`dotnet:proto`.

Sources: Microsoft's web API tutorial (`TodoItem` / `TodoItemDTO`) and dotnet/eShop (`Order`, `OrderSummary`).
