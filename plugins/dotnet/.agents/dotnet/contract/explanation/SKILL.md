---
name: explanation
description: How C# is quoted when explaining .NET code. Use when an explanation shows C# source.
kind: contract
domain: dotnet
profile: core
applicability: all C# and .NET code
requires: none
provenance: house
---

# Explaining .NET code

Owns how C# is quoted in an explanation.

Quote each file in its own top-level `csharp` block, never indented inside a list item, under a
`path:line` line. Copy the code verbatim and replace usings, namespace wrappers, DI registration and
other lines the point does not need with `...`.

`Infrastructure/Repositories/OrderRepository.cs:42`

```csharp
...
public async Task<Order?> FindAsync(OrderId id, CancellationToken cancellationToken)
{
    return await dbContext.Orders.FindAsync([id.Value], cancellationToken);
}
```
