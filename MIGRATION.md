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
