# Source ownership and generation

`.agents/` is the only authored home for host-neutral .NET capabilities. This single-scope repository uses
`.agents/<kind>/<name>/SKILL.md`; it does not repeat a `dotnet/` wrapper because the repository already supplies
that scope. A definition contains the full instruction body and applicability metadata.

`.agents/plugins/manifests/` contains authored Codex and Claude manifest inputs. `.codex/` contains Codex-only
generated discovery entries. `.claude/` contains Claude configuration plus generated discovery entries. Host
discovery files never become a second authored definition.

`plugins/dotnet/` is a generated self-contained distribution. The two root marketplace files and `.agents/INDEX.md`
are generated too. Edit no generated body. Regenerate with `pwsh .agents/sync-generated.ps1` and prove zero drift
with `pwsh .agents/sync-generated.ps1 -Check`.
