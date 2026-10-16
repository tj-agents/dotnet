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
- Repair link: core PR #219, https://github.com/tj-agents/core/pull/219. Its reviewed source adds
  strict opt-in `configuration.core.auto_approve_design` and shared startup/prompt guidance for both hosts.
  PR #219 merged on 2026-10-12 as `5f8767504d211c1d5ca657f7c6b66ed55400b995`.
  This is separate from `core.auto_merge`.
- Next action: adopt the merged setting and affected learning/convention
  guidance in selected tj-agents repositories. Track broader rollout with tj-agents/docs; this scaffold
  has not installed or enabled repository settings or machine permissions.
- Resolution condition: the setting is documented and composed into both host guidance; an opted-in
  tj-agents scaffold proceeds without a repeated layout-approval question, while explicit user gates,
  scope limits and actual publication/installation authority remain enforceable. Document rollout to
  selected tj-agents repositories without claiming installation merely from source changes.
- Verification evidence: this goal's original human gate, dotnet:learning's convention procedure,
  .agents/delivery-authorization.json, and Tommy's 2026-10-12 instruction to record debt and continue.

## D002: Exclude private delivery state from local Template conformance

- Kind: debt.
- Observed/reported: 2026-10-12. The pinned kit1.2.1 checker rejects the gitignored
  `.agents/persistent-workflow-binding.json` in an active delivery checkout as outside its plugin layout.
  The same checker passes the exact immutable tracked candidate, which excludes this private runtime file.
- Impact and priority: P3; local validation reports a layout error while source/package conformance passes.
- Source owner: Template layout checking; the binding itself is owned by engineering delivery.
- State: open.
- Repair link: Template layout checking; the current repository now consumes Template 2.0.0.
- Next action: have the layout owner distinguish ignored private runtime state from shipped plugin assets,
  then adopt the resulting Template version through its normal updater.
- Resolution condition: both an active checkout with delivery state and its tracked candidate pass the
  pinned checker, while unexpected authored/package files still fail.
- Verification evidence: checks of active Docs/ScaffoldLayout and Feature/ScriptedScaffold reported that
  single path; their frozen tracked trees passed kit1.2.1 without changing or weakening the checker.
