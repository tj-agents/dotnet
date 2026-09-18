# dotagents working rules

This repository owns generic .NET contracts delivered as dotnet@dotagents. Read ARCHITECTURE.md before
changing structure.

Every canonical skill must declare kind: contract and route to one standards document. Run
pwsh .agents/sync-generated.ps1 -Check before delivery. A change is incomplete unless the generated Claude
and Codex plugin payload remains equivalent.
