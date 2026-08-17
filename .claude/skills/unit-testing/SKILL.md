---
name: unit-testing
description: Unit-test standard for .NET — what makes a test a unit test at all (no database, host factory, containers, fixtures, or HTTP), xUnit `[Fact]`/`[Theory]` shape with the expected value last, sealed public test classes in the project's root namespace, Arrange/Act/Assert separated by blank lines rather than comments, `Method_Scenario_ExpectedBehaviour` naming, building the SUT in the test constructor as a `this.`-qualified readonly field, preferring real collaborators over mocks except at genuine boundaries, one assertion library per tier, regions named for the method under test, and expressing an architecture-guard allowlist as a self-verifying `TheoryData`. Use when adding or reviewing a unit test, deciding whether a test belongs in the unit or integration suite, or adding a temporary exclusion to a repo-wide guard test.
---

# unit-testing

This is a Claude Code compatibility stub. Do not edit skill instructions here.

Read and follow the canonical agent-agnostic skill at ../../../.agents/skills/unit-testing/SKILL.md.
