from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS_DIR = ROOT / ".agents" / "tests" / "snippets"
CONTRACTS_ROOT = ROOT / ".agents" / "dotnet" / "contract"

sys.path.insert(0, str(SNIPPETS_DIR))
from manifest import SNIPPETS  # noqa: E402
import gen_snippets  # noqa: E402

FENCE = re.compile(r"```csharp\n(.*?)\n```", re.DOTALL)


class SnippetFixtureTests(unittest.TestCase):
    def test_every_csharp_block_is_covered_by_the_manifest(self) -> None:
        covered: dict[str, set[int]] = {}
        for snippet in SNIPPETS:
            covered.setdefault(snippet["skill"], set()).add(snippet["block"])
        for skill_path in sorted(CONTRACTS_ROOT.rglob("SKILL.md")):
            relative = skill_path.relative_to(CONTRACTS_ROOT).as_posix()
            count = len(FENCE.findall(skill_path.read_text(encoding="utf-8")))
            if count == 0:
                continue
            expected = set(range(1, count + 1))
            actual = covered.get(relative, set())
            self.assertEqual(expected, actual, f"{relative} has {count} csharp blocks; manifest covers {sorted(actual)}")

    def test_fixture_snippet_region_is_byte_identical_to_its_skill_md_block(self) -> None:
        for snippet in SNIPPETS:
            if snippet["skip"]:
                continue
            with self.subTest(id=snippet["id"]):
                skill_path = CONTRACTS_ROOT / snippet["skill"]
                expected = gen_snippets.extract_block(skill_path, snippet["block"])
                fixture_path = SNIPPETS_DIR / snippet["project"] / f"{snippet['id']}.Snippet.cs"
                self.assertTrue(fixture_path.is_file(), f"missing fixture: {fixture_path}")
                actual = gen_snippets.region(fixture_path.read_text(encoding="utf-8"))
                self.assertEqual(expected, actual, f"{fixture_path} has drifted from {skill_path} block {snippet['block']}")

    def test_fixtures_are_not_stale(self) -> None:
        self.assertEqual(0, gen_snippets.write_or_check(check=True))

    def test_skipped_snippets_each_carry_a_reason(self) -> None:
        for snippet in SNIPPETS:
            if snippet["skip"] is not None:
                self.assertTrue(snippet["skip"].strip(), snippet["id"])

    def test_snippet_ids_are_unique(self) -> None:
        ids = [snippet["id"] for snippet in SNIPPETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_project_value_is_a_known_kind(self) -> None:
        known = {"infrastructure", "web", "unit-tests", "integration-tests", "e2e-tests"}
        for snippet in SNIPPETS:
            self.assertIn(snippet["project"], known, snippet["id"])


if __name__ == "__main__":
    unittest.main()
