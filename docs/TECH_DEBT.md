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
