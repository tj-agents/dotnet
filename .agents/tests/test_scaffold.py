from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".agents" / "dotnet" / "utility" / "scaffold" / "scripts" / "scaffold.py"
SPECIFICATION = importlib.util.spec_from_file_location("dotnet_scaffold", SCRIPT)
if SPECIFICATION is None or SPECIFICATION.loader is None:
    raise RuntimeError("cannot load dotnet scaffold")
SCAFFOLD = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(SCAFFOLD)


class ScaffoldTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def create(self, directory: Path, name: str, preset: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli("new", "--name", name, "--destination", str(directory), "--preset", preset)

    def test_config_and_set_precedence_report_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "options.json"
            config.write_text(
                json.dumps({"architecture": "single-service", "data": "none", "database": "none", "tests": []}),
                encoding="utf-8",
            )

            result = self.run_cli(
                "new",
                "--name",
                "Example",
                "--destination",
                str(root),
                "--preset",
                "api",
                "--config",
                str(config),
                "--set",
                "data=efcore",
                "--set",
                "database=postgres",
                "--set",
                'tests=["unit"]',
                "--dry-run",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual("--set", output["options"]["data"]["source"])
            self.assertEqual("--set", output["options"]["database"]["source"])
            self.assertEqual("--set", output["options"]["tests"]["source"])
            self.assertEqual("config", output["options"]["architecture"]["source"])

    def test_invalid_names_types_and_dependencies_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid_name = self.run_cli("new", "--name", "bad-name", "--destination", str(root))
            invalid_type = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", "selected-stack=true"
            )
            invalid_dependency = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", "data=none"
            )
            invalid_array = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", 'hosts=[]'
            )
            duplicate_array = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", "hosts=[api,api]"
            )

            self.assertEqual(2, invalid_name.returncode)
            self.assertEqual(2, invalid_type.returncode)
            self.assertEqual(2, invalid_dependency.returncode)
            self.assertEqual(2, invalid_array.returncode)
            self.assertEqual(2, duplicate_array.returncode)

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            result = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--preset", "minimal", "--dry-run"
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse((root / "Example").exists())
            self.assertIn("src/Example.Api/Program.cs", json.loads(result.stdout)["files"])

    def test_literal_home_destination_expands_without_writing(self) -> None:
        name = f"ScaffoldHome{uuid4().hex}"
        project = Path.home() / name
        self.assertFalse(project.exists())

        result = self.run_cli("new", "--name", name, "--destination", "~", "--preset", "minimal", "--dry-run")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(str(project), json.loads(result.stdout)["destination"])
        self.assertFalse(project.exists())

    def test_csharp_intrinsics_are_rejected_in_every_namespace_segment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for intrinsic in ("__arglist", "__makeref", "__reftype", "__refvalue"):
                for name in (intrinsic, f"Example.{intrinsic}"):
                    result = self.run_cli("new", "--name", name, "--destination", str(root), "--dry-run")

                    self.assertEqual(2, result.returncode, result.stderr)
                    self.assertFalse((root / name).exists())

    def test_existing_project_and_non_directory_destination_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Example").mkdir()
            file = root / "destination.txt"
            file.write_text("destination", encoding="utf-8")

            existing = self.run_cli("new", "--name", "Example", "--destination", str(root))
            non_directory = self.run_cli("new", "--name", "Other", "--destination", str(file))

            self.assertEqual(1, existing.returncode)
            self.assertEqual(1, non_directory.returncode)

    def test_competing_project_root_is_refused_before_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            with mock.patch.object(Path, "mkdir", side_effect=FileExistsError):
                with self.assertRaises(SCAFFOLD.ScaffoldError):
                    SCAFFOLD.output(root, "Example", {"file.txt": "content\n"}, {}, {}, False)

            self.assertFalse((root / "Example").exists())

    def test_generated_files_use_lf_and_resolve_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create(root, "Example", "api")

            self.assertEqual(0, result.returncode, result.stderr)
            for path in (root / "Example").rglob("*"):
                if path.is_file():
                    content = path.read_bytes()
                    self.assertNotIn(b"\r\n", content, path)
                    self.assertNotIn(b"$NAME$", content, path)
                    self.assertNotIn(b"$FRAMEWORK$", content, path)
                    self.assertNotIn(b"$SOLUTION_PROJECTS$", content, path)

    def test_presets_generate_exact_file_lists(self) -> None:
        expected = {
            "minimal": [
                ".editorconfig",
                ".gitattributes",
                ".github/workflows/ci.yml",
                ".gitignore",
                ".scaffold.json",
                "AGENTS.md",
                "CLAUDE.md",
                "Directory.Build.props",
                "Directory.Packages.props",
                "Example.slnx",
                "global.json",
                "src/Example.Api/Example.Api.csproj",
                "src/Example.Api/Program.cs",
                "src/Example.Api/appsettings.json",
                "src/Example.Core/Example.Core.csproj",
            ],
            "api": [
                ".editorconfig",
                ".gitattributes",
                ".github/workflows/ci.yml",
                ".gitignore",
                ".scaffold.json",
                "AGENTS.md",
                "CLAUDE.md",
                "Directory.Build.props",
                "Directory.Packages.props",
                "Example.slnx",
                "global.json",
                "src/Example.Api/Example.Api.csproj",
                "src/Example.Api/Program.cs",
                "src/Example.Api/appsettings.json",
                "src/Example.Core/Example.Core.csproj",
                "src/Example.Infrastructure/Example.Infrastructure.csproj",
                "src/Example.Infrastructure/Persistence/ApplicationDbContext.cs",
                "src/Example.Infrastructure/ServiceCollectionExtensions.cs",
                "tests/Example.UnitTests/Example.UnitTests.csproj",
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for preset, expected_files in expected.items():
                name = "Example" if preset == "minimal" else "ExampleApi"
                result = self.create(root, name, preset)

                self.assertEqual(0, result.returncode, result.stderr)
                generated = sorted(
                    path.relative_to(root / name).as_posix() for path in (root / name).rglob("*") if path.is_file()
                )
                rewritten = [item.replace("Example", name) for item in expected_files]
                self.assertEqual(rewritten, generated)


if __name__ == "__main__":
    unittest.main()
