# Plugin layout migration

The repository now uses [Template](https://github.com/tj-agents/template)'s layout: skills live under
`.agents/dotnet/<kind>/`, related skills share a family folder, family first, and a skill's name is its folder
path joined by hyphens. Each required standard contract is a stack-free `core` skill; the opinionated guidance
it replaces is a family member that keeps its original profile and prerequisite.

Old names no longer resolve. Update references to the new names.

| Old | New |
|---|---|
| `dotnet:csharp-naming` | `dotnet:naming` |
| `dotnet:csharp-style` | `dotnet:style` |
| `dotnet:style-comments` | `dotnet:comments` |
| `dotnet:naming-mapping` | `dotnet:mapping` |
| `dotnet:naming-repositories` | `dotnet:repositories` |
| `dotnet:module-structure` | `dotnet:structure-modules` |
| `dotnet:ddd` | `dotnet:domain-ddd` |
| `dotnet:value-semantics` | `dotnet:domain-values` |
| `dotnet:result-errors` | `dotnet:errors-results` |
| `dotnet:result-carriers` | `dotnet:errors-carriers` |
| `dotnet:result-terminals` | `dotnet:errors-terminals` |
| `dotnet:unit-testing` | `dotnet:testing-unit` |
| `dotnet:integration-testing` | `dotnet:testing-integration` |
| `dotnet:e2e-scenarios` | `dotnet:testing-e2e` |
| `dotnet:stack`, `dotnet:dotnet-stack` | `dotnet:libraries-selected` |
| `dotnet:integration-debug` | `dotnet:debug-integration` |
| `dotnet:e2e-debug` | `dotnet:debug-e2e` |
| `dotnet:e2e-api-debug` | `dotnet:debug-e2e-api` |
| `dotnet:e2e-ui-debug` | `dotnet:debug-e2e-ui` |

`dotnet:domain-events`, `dotnet:keyed-strategies` and `dotnet:keyed-unions` keep their names inside their families.
`dotnet:fields` and `dotnet:messaging` are new: `fields` takes field naming, `this.`, `base.` and
primary-constructor rules from `dotnet:style`; `messaging` takes the publisher and processor roles from
`dotnet:naming-collaborators` and `dotnet:microservice-boundaries`.

## EF Core namespace

EF Core-specific contracts now publish from `efcore@tj-agents` in this repository. Its dependency on
`dotnet@tj-agents` retains generic C# conventions. Consumers using the central `tj-agents` marketplace
select `efcore@tj-agents`; refresh their composed catalog/harness and generated route tables together.
No old-name forwarding skills remain.

| Old | New |
|---|---|
| `dotnet:persistence` | `efcore:persistence` |
| `dotnet:multitenancy` | `efcore:multitenancy` |
| EF SaveChanges portion of `dotnet:domain-events` | `efcore:event-dispatch` |

`dotnet:domain-events` keeps generic event raising, handler registration and integration-event translation.
`dotnet:seeding` keeps production-write ownership, canonical seed state and idempotency independently of an
ORM; its EF persistence example moved to `efcore:persistence`. Query patterns are newly canonical under
`efcore:specification` and `efcore:query-building`. Repository contracts remain `dotnet:repositories`.

With two source plugins, repository-local host discovery adapters are qualified (`dotnet-scaffold`,
`efcore-specification`); installed per-plugin public names remain `dotnet:scaffold`, `efcore:specification`.
