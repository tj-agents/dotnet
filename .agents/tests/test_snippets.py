from __future__ import annotations

import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS_DIR = ROOT / ".agents" / "dotnet" / "utility" / "scaffold" / "snippets"
CONTRACTS_ROOT = ROOT / ".agents" / "dotnet" / "contract"

sys.path.insert(0, str(SNIPPETS_DIR))
from manifest import SNIPPETS  # noqa: E402
import gen_snippets  # noqa: E402

VERIFY_PATH = ROOT / ".agents" / "dotnet" / "utility" / "scaffold" / "scripts" / "verify.py"
GENERATED_VERIFY_PATHS = (
    ROOT / ".claude" / "skills" / "dotnet-scaffold" / "scripts" / "verify.py",
    ROOT / ".codex" / "skills" / "dotnet-scaffold" / "scripts" / "verify.py",
    ROOT / "plugins" / "dotnet" / "skills" / "scaffold" / "scripts" / "verify.py",
)


def load_verify(path: Path):
    specification = importlib.util.spec_from_file_location("snippet_verify", path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load scaffold verification gate: {path}")
    verifier = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(verifier)
    return verifier


FENCE = re.compile(r"```csharp\n(.*?)\n```", re.DOTALL)

FAKE_STANDARDS_ADOPTER = textwrap.dedent(
    """
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--plugin", action="append", default=[])
    parser.add_argument("--mode", required=True)
    args = parser.parse_args()
    root = Path(args.root)
    plugins = ["base@tj-agents", "engineering@tj-agents", "machine@tj-agents", "dotnet@tj-agents"]
    plugins.extend(plugin for plugin in args.plugin if plugin not in plugins)
    files = {
        ".agents/plugins.json": json.dumps({"schema_version": 1, "marketplaces": {"tj-agents": {"repository": "tj-agents/marketplace"}}, "plugins": plugins}) + "\\n",
        ".claude/settings.json": "{}\\n",
        ".codex/config.toml": "[plugins]\\n",
    }
    if args.mode == "write":
        for relative, content in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    """
)


class SnippetFixtureTests(unittest.TestCase):
    def test_every_csharp_block_is_covered_by_the_manifest(self) -> None:
        covered: dict[tuple[str, str], set[int]] = {}
        for snippet in SNIPPETS:
            covered.setdefault((snippet["owner"], snippet["skill"]), set()).add(snippet["block"])
        for owner, contracts in gen_snippets.contract_roots().items():
            for skill_path in sorted(contracts.rglob("SKILL.md")):
                relative = skill_path.relative_to(contracts).as_posix()
                count = len(FENCE.findall(skill_path.read_text(encoding="utf-8")))
                if count == 0:
                    continue
                expected = set(range(1, count + 1))
                actual = covered.get((owner, relative), set())
                self.assertEqual(expected, actual, f"{owner}:{relative} has {count} csharp blocks; manifest covers {sorted(actual)}")

    def test_fixture_snippet_region_is_byte_identical_to_its_skill_md_block(self) -> None:
        for snippet in SNIPPETS:
            if snippet["skip"]:
                continue
            with self.subTest(id=snippet["id"]):
                skill_path = gen_snippets.contract_path(snippet, gen_snippets.contract_roots())
                expected = gen_snippets.extract_block(skill_path, snippet["block"])
                fixture_path = SNIPPETS_DIR / snippet["project"] / f"{snippet['id']}.Snippet.cs"
                self.assertTrue(fixture_path.is_file(), f"missing fixture: {fixture_path}")
                actual = gen_snippets.region(fixture_path.read_text(encoding="utf-8"))
                self.assertEqual(expected, actual, f"{fixture_path} has drifted from {skill_path} block {snippet['block']}")

    def test_fixtures_are_not_stale(self) -> None:
        self.assertEqual(0, gen_snippets.write_or_check(check=True))

    def test_packaged_snippet_generation_uses_the_separate_efcore_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            payloads = Path(temporary)
            for owner in ("dotnet", "efcore"):
                shutil.copytree(ROOT / "plugins" / owner, payloads / owner)
            dotnet = payloads / "dotnet"
            self.assertFalse((dotnet / ".agents/efcore").exists())
            scripts = (
                dotnet / ".agents/dotnet/utility/scaffold/snippets/gen_snippets.py",
                dotnet / "skills/scaffold/snippets/gen_snippets.py",
            )
            for script in scripts:
                with self.subTest(script=script):
                    result = subprocess.run([sys.executable, "-B", str(script), "--check"], cwd=payloads, capture_output=True, text=True)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            separate = payloads / "separate-cache" / "efcore-version"
            separate.parent.mkdir()
            (payloads / "efcore").rename(separate)
            missing = subprocess.run([sys.executable, "-B", str(scripts[0]), "--check"], cwd=payloads, capture_output=True, text=True)
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("--contract-root efcore=", missing.stderr)
            bound = subprocess.run(
                [sys.executable, "-B", str(scripts[0]), "--check", "--contract-root", f"efcore={separate / '.agents/efcore/contract'}"],
                cwd=payloads, capture_output=True, text=True,
            )
            self.assertEqual(0, bound.returncode, bound.stdout + bound.stderr)
            self.assertFalse((dotnet / ".agents/efcore").exists())

    def test_generated_verifiers_resolve_the_complete_shipped_snippet_assets(self) -> None:
        expected_files = {
            path.relative_to(SNIPPETS_DIR): path.read_bytes()
            for path in SNIPPETS_DIR.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        }
        for path in GENERATED_VERIFY_PATHS:
            with self.subTest(verifier=path):
                verifier = load_verify(path)
                self.assertEqual(path.parents[1] / "snippets", verifier.SNIPPETS_DIR)
                actual_files = {
                    item.relative_to(verifier.SNIPPETS_DIR): item.read_bytes()
                    for item in verifier.SNIPPETS_DIR.rglob("*")
                    if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc"
                }
                self.assertEqual(expected_files, actual_files)

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
                top, suffix = verifier.SNIPPET_PROJECT_FOLDERS[snippet["project"]]
                self.assertTrue((project / top / f"{name}.{suffix}" / "Snippets" / f"{snippet['id']}.Snippet.cs").is_file())

        with tempfile.TemporaryDirectory() as temporary:
            standards_root = Path(temporary)
            adopter = standards_root / "adopt_plugins.py"
            adopter.write_text(FAKE_STANDARDS_ADOPTER, encoding="utf-8")
            environment = {"PLUGIN_SELECTION_ADOPTER": str(adopter)}
            for path in (VERIFY_PATH, *GENERATED_VERIFY_PATHS):
                with self.subTest(verifier=path):
                    verifier = load_verify(path)
                    with (
                        mock.patch.dict(os.environ, environment, clear=False),
                        mock.patch.object(verifier, "run", side_effect=run),
                        redirect_stdout(io.StringIO()),
                    ):
                        verifier.snippet_compile_gate(name)
        self.assertEqual(4, build_count)

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
