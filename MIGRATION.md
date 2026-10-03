# Migration to kit 1.1.0

The repository now uses [kit](https://github.com/tj-agents/kit)'s layout: skills live under
`.agents/dotnet/<kind>/`, related skills share a family folder, family first, and a skill's name is its folder
path joined by hyphens. Each required standard contract is a stack-free `core` skill; the opinionated guidance
it replaces is a family member that keeps its original profile and prerequisite.

These old names remain forwarding aliases until 2027-03-31. Update references to the new names.

| Old | New |
|---|---|
| `dotnet:csharp-naming` | `dotnet:naming` |
| `dotnet:csharp-style` | `dotnet:style` |
| `dotnet:comments` | `dotnet:style-comments` |
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
`dotnet:naming-collaborators`, `dotnet:naming-repositories`, `dotnet:naming-data-contracts` and
`dotnet:naming-mapping` are new; they replace the single broad naming skill's sections.
