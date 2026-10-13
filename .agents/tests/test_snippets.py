from __future__ import annotations

import importlib.util
import io
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS_DIR = ROOT / ".agents" / "tests" / "snippets"
CONTRACTS_ROOT = ROOT / ".agents" / "dotnet" / "contract"

sys.path.insert(0, str(SNIPPETS_DIR))
from manifest import SNIPPETS  # noqa: E402
import gen_snippets  # noqa: E402

VERIFY_PATH = ROOT / ".agents" / "dotnet" / "utility" / "scaffold" / "scripts" / "verify.py"
SPECIFICATION = importlib.util.spec_from_file_location("snippet_verify", VERIFY_PATH)
if SPECIFICATION is None or SPECIFICATION.loader is None:
    raise RuntimeError("cannot load scaffold verification gate")
VERIFY = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(VERIFY)

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

    def test_compile_gate_adds_the_e2e_project_with_pinned_dependencies_and_verbatim_fixture(self) -> None:
        name = "SnippetHarnessSample"
        build_count = 0

        def run(command, cwd):
            nonlocal build_count
            if command[0] != "dotnet":
                subprocess.run(command, cwd=cwd, check=True, capture_output=True)
                return
            if command[1] != "build":
                return
            build_count += 1
            project = Path(cwd)
            e2e_dir = project / "tests" / f"{name}.E2ETests"
            csproj = ElementTree.parse(e2e_dir / f"{name}.E2ETests.csproj").getroot()
            self.assertEqual("true", csproj.findtext("PropertyGroup/IsTestProject"))
            packages = {
                item.get("Include"): item.get("Version")
                for item in ElementTree.parse(project / "Directory.Packages.props").iter("PackageVersion")
            }
            for package, version in (
                ("Reqnroll", "3.3.4"), ("Reqnroll.xUnit", "3.3.4"),
                ("Microsoft.Playwright", "1.63.0"), ("Shouldly", "4.3.0"),
            ):
                self.assertEqual(version, packages[package])
                self.assertIsNotNone(csproj.find(f"ItemGroup/PackageReference[@Include='{package}']"))
            solution = ElementTree.parse(project / f"{name}.slnx")
            self.assertIsNotNone(solution.find(f"Project[@Path='tests/{name}.E2ETests/{name}.E2ETests.csproj']"))
            fixture = e2e_dir / "Snippets" / "testing-e2e-01-clock.Snippet.cs"
            self.assertEqual(
                gen_snippets.extract_block(CONTRACTS_ROOT / "testing/e2e/SKILL.md", 1),
                gen_snippets.region(fixture.read_text(encoding="utf-8")),
            )
            self.assertTrue((e2e_dir / "Snippets" / "E2E.Stubs.cs").is_file())
            for snippet in SNIPPETS:
                if snippet["skip"]:
                    continue
                top, suffix = VERIFY.SNIPPET_PROJECT_FOLDERS[snippet["project"]]
                self.assertTrue((project / top / f"{name}.{suffix}" / "Snippets" / f"{snippet['id']}.Snippet.cs").is_file())

        with mock.patch.object(VERIFY, "run", side_effect=run), redirect_stdout(io.StringIO()):
            VERIFY.snippet_compile_gate(name)
        self.assertEqual(1, build_count)

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
