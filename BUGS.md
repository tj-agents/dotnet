# Bugs

## B001 — Generated routes name a missing Core skill

- Kind: bug.
- Observed/reported: 2026-10-12, PR41 exact CI38256944454 attempt1 failed `test_routed_skills_resolve_and_stay_inside_the_layers` on Windows and Linux with `engineering:docs-and-debt` missing from Core8e7110da. This generator still names that obsolete capability. The replacement ownership and dependency closure are under bounded diagnosis.
- Impact and priority: P2; generated consumer guidance is unresolved and the required verification jobs block delivery.
- Source owner: tj-agents/dotnet, `.agents/dotnet/utility/skill-routes/scripts/gen_skill_routes.py` and its shipped dependency manifest.
- State: in-progress.
- Repair link: Chore/RepositoryAutoMerge, PR41; the existing twelve-repository auto-merge rollout owns this causal recovery.
- Next action: authenticate the current published documentation/debt owners, update only their routes and causal declared dependencies, then run the unchanged resolution assertion against the same Core revision as CI.
- Resolution condition: generated routes resolve to the current published owning skills for both host projections; the complete repository suite and exact repaired-head Windows/Linux/hosts CI pass without weaker assertions, skips or dependency rollback.
- Verification evidence: exact failure log `.git/agent-workflow/runs/dotnet-optin-ci-diagnosis-41/artifacts/105d3ee319db7a12-exact-pr-ci-failed.log`; last real Linux pass38060290382/job114237006429 ran16 tests in0.335s against Core33fb415 on2026-10-10, captured as `1a8a1f5ab515219c-last-real-main-linux-pass.log`. Current local16-test pass used stale primary Core and does not establish current-dependency compatibility.
