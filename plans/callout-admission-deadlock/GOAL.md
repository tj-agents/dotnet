# Repair the callout-admission deadlock

## Scope

Repair the shared callout enforcement path so a called-out session can complete `engineering:self-repair` admission and bounded source handoff without bypassing safety checks.

Repair workflow: engineering:self-repair

Source owner: shared engineering callout PreToolUse/Stop enforcement and engineering:self-repair/engineering:handoff admission workflow

Callout session: 01a1362c-5751-75f3-a54d-9bb37f25a41a

Callout id: 9c4f5441-05ea-4f6c-8928-b4ad73154ef1

Prompt SHA256: 6f4ed91c3a8224e79afdb944f48f7c7783b0703d04075ac947b59bc3340ac34c

Problem record: C:\Users\TommySeery\source\repos\tj-agents\dotnet\BUGS.md#B009

## Authorization

The standing standards-defect authorization in `engineering:session-guidance` authorizes this bounded source repair through normal delivery gates. The user explicitly requires the current CLI and worktree to remain open.

## Observed blocker

The installed classifier blocks an output-only PowerShell read pipeline and a quoted validator path, although both are required to establish the repair disposition. The validator’s deferred-capability evidence equates an available Python executable with a usable admission path. Stop then replays its generated hook content as a user turn.

Required executable: callout-admission-gate

## Acceptance criteria

The repaired classifier admits declared read-only output pipelines and exact validator commands while continuing to reject unrelated mutation. Deferred evidence can represent host denial of an available executable. A repeated `(session_id, callout_id, prompt_sha256)` event creates no response, record update, command, or successor. Wait uses a bound durable monitor only for an owned delivery, otherwise quiet idle.

## Next steps

1. Reproduce read-pipeline, quoted-validator, evidence-model, and stale-hook behavior from the shared source checkout.
2. Add focused regressions for the allowed bounded forms, a denied unrelated command, gate-denial evidence, and replay idempotency.
3. Implement, generate affected outputs, review, and deliver through normal workflow.
