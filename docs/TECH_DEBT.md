# Technical debt

## D001: Honor configured design approval across agent hosts

- Kind: debt.
- Observed/reported: 2026-10-12. Tommy expected repository configuration to avoid routine design
  approval. This scaffold handoff and dotnet:learning required a second layout decision despite
  explicit implementation/delivery authorization. The existing recorded auto-merge setting only
  covers delivery; no equivalent convention-delegation setting was observed in this checkout.
- Impact and priority: P2; repeated prompts interrupt authorized tj-agents work on Claude and Codex.
- Source owner: shared repository configuration in tj-agents/core; dotnet owns learning/convention
  adoption. Cross-repository design documentation belongs in tj-agents/docs.
- State: open.
- Repair link: C:/Users/TommySeery/source/repos/tj-agents/core/.worktrees/Fix-ConventionApprovalConfiguration/plans/convention-approval-configuration/GOAL.md
  (successor acknowledged pickup on 2026-10-12; core source repair active).
- Next action: define one portable opt-in setting for delegated routine design/convention decisions
  and make both hosts and affected stack learning contracts honor it within existing task authority.
- Resolution condition: the setting is documented and composed into both host guidance; an opted-in
  tj-agents scaffold proceeds without a repeated layout-approval question, while explicit user gates,
  scope limits and actual publication/installation authority remain enforceable. Document rollout to
  selected tj-agents repositories without claiming installation merely from source changes.
- Verification evidence: this goal's original human gate, dotnet:learning's convention procedure,
  .agents/delivery-authorization.json, and Tommy's 2026-10-12 instruction to record debt and continue.


## D003: Use focused interim checks and one final full CI run

- Kind: debt.
- Observed/reported: 2026-10-12. Scripted scaffold delivery spent excessive time and tokens on repeated broad qualification and workflow bookkeeping. Tommy explicitly requires interim tests selected for the changes made, followed by one full CI run at the end of the finished implementation; a small local commit is not a validation boundary.
- Impact and priority: P1; the delivery took roughly six hours and repeatedly interrupted useful implementation.
- Source owner: tj-agents/dotnet scaffold workflow for execution cadence; tj-agents/core engineering owns shared test selection, commit/push cadence and final-record choreography.
- State: in-progress.
- Repair link: .worktrees/Fix-InertCloseoutCadence/plans/inert-closeout-cadence/GOAL.md (isolated core successor acknowledged pickup); core BUGS.md B008 records the confirmed immediate-doc-commit versus exact-head-closeout policy collision.
- Next action: preserve focused interim tests for changed behavior; batch small commits locally; run the full matrix once on the finished candidate. Remove bookkeeping-only validation cycles and duplicate push/PR matrix runs. Coordinate shared-source enforcement and consumer adoption without changing installed global settings.
- Resolution condition: both agent hosts choose tests from affected behavior, avoid full local matrices after small commits, and submit one final full CI candidate after batched implementation; inert notes never invalidate green executable validation or restart its matrix. A genuine failure or later functional change is repaired with targeted checks and validated on the resulting final candidate.
- Verification evidence: final scaffold head8f22d5d passed36 repository tests and all seven configurations on Windows/Ubuntu. Scaffold push38303051185 and PR38303056095 duplicated the full matrix for one SHA. The contemplated record-only extra push was cancelled before execution. Core remote-validation already prohibits that extra push; agent misapplication and the adjacent conflicting closeout rule require enforcement repair.

