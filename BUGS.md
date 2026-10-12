# Bugs

## B001

- **Kind:** bug
- **Observed/reported:** 2026-10-12 — CI run 38256944454 failed on Windows and Ubuntu in `.agents/tests/test_route_cli.py:139` because route resolution included `engineering:docs-and-debt`, which is no longer a current engineering capability. Cause confirmed: the dotnet skill-route generator emits the retired capability reference.
- **Impact and priority:** current-core route generation fails in CI; P2 because it blocks affected pull requests but has no reported production impact.
- **Source owner:** `tj-agents/dotnet` `.agents/dotnet/utility/skill-routes`.
- **State:** resolved
- **Repair link:** `plans/route-capability-references/GOAL.md` and PR #44
- **Next action:** none; resolved.
- **Resolution condition:** generated routes and focused route-resolution tests pass using the same current core revision as CI.
- **Verification evidence:** `python -B -m unittest discover -s .agents/tests -p "test_*.py"` passed 16 tests against core `8e7110da37540971be623eabd847618ee32ea04c`; generated outputs were current; and PR #44 passed hosts, Ubuntu, and Windows CI before merging as `bd524c3564895e41a79d3ea2605e63eb7173a1a6`.


## B008: Continuation access failure leaves a blocked owner without a typed gate

- Kind: bug.
- Observed/reported: 2026-10-12. The continuation runtime heartbeat returned state=blocked, reason="git exited 128" during a sandboxed Git probe. The Stop prompt then reported that the blocked owner lacked a genuine typed gate. The same owner, authority, goal and PID were restored using supported yield/claim in the normal authorized execution context.
- Cause: access-dependent Git failure is observed; its exact denied operation is not yet established. Do not conflate this with the separately diagnosed binding-head normalization bug in core PR226 or the automatic approval review rejection of a composite cleanup.
- Impact and priority: P2; an internal probe failure becomes a false workflow stop and repetitive user-facing continuation friction.
- Source owner: tj-agents/core continuation runtime, Stop hook and host execution-context integration.
- State: open.
- Repair link: core hook/cache repair PR226 is related; exact Git-probe failure requires bounded diagnosis without overlapping that writer.
- Next action: diagnose the exact read/access failure; ensure recoverable internal probe errors preserve ownership and independent progress, while a genuinely blocked action carries a typed resolver, unblock action and resume condition.
- Resolution condition: a regression through the real runtime/Stop path reproduces Git128 and proves it cannot produce a blocked owner lacking its required typed gate; supported recovery retains one writer and does not ask for approval already granted.
- Verification evidence: heartbeat output state=blocked/reason=git exited128; Stop hook prompt "The blocked continuation owner lacks a genuine typed gate"; subsequent supported yield/claim restores working under identical PID16108 and owner060208e34169e293041bf3de. No external user gate was pending. Scaffold owner is now complete; PR47 is merged.

