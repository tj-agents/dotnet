from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
from uuid import uuid4
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".agents" / "dotnet" / "utility" / "scaffold" / "scripts" / "scaffold.py"
SCAFFOLD_SKILL = SCRIPT.parent.parent / "SKILL.md"
VERIFY_SCRIPT = SCRIPT.parent / "verify.py"
SPECIFICATION = importlib.util.spec_from_file_location("dotnet_scaffold", SCRIPT)
if SPECIFICATION is None or SPECIFICATION.loader is None:
    raise RuntimeError("cannot load dotnet scaffold")
SCAFFOLD = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(SCAFFOLD)
VERIFY_SPECIFICATION = importlib.util.spec_from_file_location("dotnet_scaffold_verify", VERIFY_SCRIPT)
if VERIFY_SPECIFICATION is None or VERIFY_SPECIFICATION.loader is None:
    raise RuntimeError("cannot load dotnet scaffold verification")
VERIFY = importlib.util.module_from_spec(VERIFY_SPECIFICATION)
VERIFY_SPECIFICATION.loader.exec_module(VERIFY)


FAKE_AZURE_OPTIONS = {
    "http_host": {
        "type": "string", "allowed": ["container-apps", "app-service"], "default": "container-apps",
        "description": "The http host.",
    },
    "key_vault": {
        "type": "boolean", "allowed": [False, True], "default": False, "description": "Whether to add a key vault.",
    },
}

FAKE_AZURE_SCAFFOLD = textwrap.dedent(
    """
    import argparse
    import json
    import os
    import sys
    from pathlib import Path

    def main():
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers(dest="command", required=True)
        new = commands.add_parser("new")
        new.add_argument("--into", required=True)
        new.add_argument("--profile")
        new.add_argument("--dry-run", action="store_true")
        new.add_argument("--no-input", action="store_true")
        new.add_argument("--set", action="append", default=[])
        options = commands.add_parser("options")
        options.add_argument("--preset")
        options.add_argument("--config")
        options.add_argument("--set", action="append", default=[])
        options.add_argument("--schema", action="store_true")
        args = parser.parse_args()

        log_path = os.environ.get("FAKE_AZURE_LOG")
        if log_path:
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(sys.argv[1:]) + "\\n")

        if args.command == "options":
            schema_path = Path(__file__).resolve().parent.parent / "options.json"
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if args.schema:
                print(json.dumps(schema))
                return 0
            result = {
                key: {"value": definition["default"], "source": "options.json"}
                for key, definition in schema.items()
            }
            print(json.dumps(result))
            return 0

        fail = os.environ.get("FAKE_AZURE_FAIL")
        if args.dry_run:
            if fail == "dry":
                print("fake azure dry run failure", file=sys.stderr)
                return 2
            return 0

        if fail == "real":
            print("fake azure real run failure", file=sys.stderr)
            return 1

        into = Path(args.into)
        workflow = into / ".github" / "workflows" / "ci.yml"
        if workflow.exists():
            print("ci.yml already exists at Azure handoff", file=sys.stderr)
            return 1
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("name: Azure CI\\n", encoding="utf-8")
        (into / "infra").mkdir(parents=True, exist_ok=True)
        (into / "infra" / "FAKE_AZURE_RAN.txt").write_text("ok\\n", encoding="utf-8")
        return 0

    if __name__ == "__main__":
        raise SystemExit(main())
    """
)

FAKE_STANDARDS_ADOPTER = textwrap.dedent(
    """
    import argparse
    import json
    import os
    import sys
    from pathlib import Path

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--root", required=True)
        parser.add_argument("--plugin", action="append", default=[])
        parser.add_argument("--stack", required=True)
        parser.add_argument("--mode", required=True)
        args = parser.parse_args()
        log_path = os.environ.get("FAKE_STANDARDS_LOG")
        if log_path:
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(sys.argv[1:]) + "\\n")
        if os.environ.get("FAKE_STANDARDS_FAIL"):
            print("fake standards failure", file=sys.stderr)
            return 9
        if args.mode == "check" and os.environ.get("FAKE_STANDARDS_CHECK_FAIL"):
            print("fake standards check failure", file=sys.stderr)
            return 8
        if args.mode == "check":
            return 0
        root = Path(args.root)
        plugins = ["base@tj-agents", "engineering@tj-agents", "machine@tj-agents", "dotnet@tj-agents"]
        if args.stack == "azure":
            plugins.append("azure@tj-agents")
        omitted = os.environ.get("FAKE_STANDARDS_OMIT_PLUGIN")
        if omitted:
            plugins = [plugin for plugin in plugins if plugin != omitted]
        files = {
            ".agents/plugins.json": json.dumps({"schema_version": int(os.environ.get("FAKE_STANDARDS_SCHEMA_VERSION", "1")), "marketplaces": {"tj-agents": {"repository": "tj-agents/marketplace"}}, "plugins": plugins}) + "\\n",
            ".claude/settings.json": "{}\\n",
            ".codex/config.toml": "[plugins]\\n",
            ".codex/rules/agent-harness.rules": "allow\\n",
            "standards/manifest.txt": "prepared\\n",
        }
        if os.environ.get("FAKE_STANDARDS_PIN"):
            selection = json.loads(files[".agents/plugins.json"])
            selection["marketplaces"]["tj-agents"]["revision"] = "v1.1.0"
            files[".agents/plugins.json"] = json.dumps(selection) + "\\n"
        missing = os.environ.get("FAKE_STANDARDS_MISSING")
        for relative, content in files.items():
            if relative == missing:
                continue
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return 0

    if __name__ == "__main__":
        raise SystemExit(main())
    """
)

FAKE_STANDARD_FILES = [
    ".agents/plugins.json",
    ".claude/settings.json",
    ".codex/config.toml",
    ".codex/rules/agent-harness.rules",
    "standards/manifest.txt",
]


def write_fake_azure(root: Path) -> Path:
    scripts = root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (root / "options.json").write_text(json.dumps(FAKE_AZURE_OPTIONS), encoding="utf-8")
    script = scripts / "scaffold.py"
    script.write_text(FAKE_AZURE_SCAFFOLD, encoding="utf-8")
    return script


def write_fake_standards_adopter(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    adopter = root / "adopt_repository.py"
    adopter.write_text(FAKE_STANDARDS_ADOPTER, encoding="utf-8")
    return adopter


class ScaffoldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.standards_temporary = tempfile.TemporaryDirectory()
        self.standards_adopter = write_fake_standards_adopter(Path(self.standards_temporary.name))

    def tearDown(self) -> None:
        self.standards_temporary.cleanup()

    def standards_arguments(self) -> list[str]:
        return ["--plugin-adopter", str(self.standards_adopter)]

    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        arguments = list(args)
        if arguments[:1] == ["new"] and "--no-input" not in arguments:
            arguments.append("--no-input")
        if arguments[:1] == ["new"] and "--plugin-adopter" not in arguments:
            arguments.extend(self.standards_arguments())
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            stdin=subprocess.DEVNULL,
            env=env,
        )

    def create(self, directory: Path, name: str, preset: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli("new", "--name", name, "--destination", str(directory), "--preset", preset)

    def create_with_options(
        self, directory: Path, name: str, preset: str, *overrides: str
    ) -> subprocess.CompletedProcess[str]:
        arguments = ["new", "--name", name, "--destination", str(directory), "--preset", preset]
        for override in overrides:
            arguments.extend(["--set", override])
        return self.run_cli(*arguments)

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
                "web",
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
                "new", "--name", "Example", "--destination", str(root), "--set", 'selected-stack="true"'
            )
            invalid_dependency = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", "data=none"
            )
            invalid_conflict = self.run_cli(
                "new",
                "--name",
                "Example",
                "--destination",
                str(root),
                "--set",
                "data=dapper",
                "--set",
                "database=sqlserver",
                "--set",
                "selected-stack=true",
            )
            invalid_array = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", 'hosts=[]'
            )
            duplicate_array = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--set", "hosts=[web,web]"
            )

            self.assertEqual(2, invalid_name.returncode)
            self.assertEqual(2, invalid_type.returncode)
            self.assertEqual(2, invalid_dependency.returncode)
            self.assertEqual(2, invalid_conflict.returncode)
            self.assertEqual(2, invalid_array.returncode)
            self.assertEqual(2, duplicate_array.returncode)

    def test_program_root_names_are_rejected_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("Program", "Program.Example"):
                result = self.run_cli("new", "--name", name, "--destination", str(root))

                self.assertEqual(2, result.returncode, result.stderr)
                self.assertFalse((root / name).exists())

            allowed = self.run_cli("new", "--name", "Example.Program", "--destination", str(root), "--dry-run")

            self.assertEqual(0, allowed.returncode, allowed.stderr)

    def test_array_constraint_rules_support_future_host_dependencies(self) -> None:
        option_schema = {
            "hosts": {
                "requires": {},
                "conflicts": {},
                "constraints": [
                    {"when": {"hosts": {"contains": "durable"}}, "requires": {"hosts": {"contains": "functions"}}}
                ],
            }
        }

        SCAFFOLD.validate_constraints({"hosts": ["functions", "durable"]}, option_schema)
        with self.assertRaises(SCAFFOLD.ValidationError):
            SCAFFOLD.validate_constraints({"hosts": ["durable"]}, option_schema)

    def test_component_append_and_scalar_collisions_are_rejected(self) -> None:
        options = {key: definition["default"] for key, definition in SCAFFOLD.schema().items()}
        web = (
            "web",
            SCAFFOLD.read_json(SCAFFOLD.COMPONENTS / "web" / "component.json", "component web"),
            SCAFFOLD.COMPONENTS / "web",
        )
        appended = [
            web,
            ("first", {"append": {"WEB_USINGS": "using First;"}, "projects": []}, ROOT),
            ("second", {"append": {"WEB_USINGS": "using Second;"}, "projects": []}, ROOT),
        ]
        collisions = [
            ("first", {"variables": {"OWNER": "first"}, "projects": []}, ROOT),
            ("second", {"variables": {"OWNER": "second"}, "projects": []}, ROOT),
        ]

        with mock.patch.object(SCAFFOLD, "selected_components", return_value=appended):
            files = SCAFFOLD.plan("Example", options, None)

        self.assertIn("using First;\nusing Second;", files["src/Example.Web/Program.cs"])
        with mock.patch.object(SCAFFOLD, "selected_components", return_value=collisions):
            with self.assertRaises(SCAFFOLD.ScaffoldError):
                SCAFFOLD.plan("Example", options, None)

    def test_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            result = self.run_cli(
                "new", "--name", "Example", "--destination", str(root), "--preset", "minimal", "--dry-run"
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse((root / "Example").exists())
            self.assertIn("src/Example.Web/Program.cs", json.loads(result.stdout)["files"])

    def test_new_requires_adopter_and_rejects_retired_pin_argument(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing_flags = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "new", "--name", "Missing", "--destination", str(root), "--no-input"],
                cwd=ROOT, capture_output=True, text=True,
            )
            missing_adopter = self.run_cli(
                "new", "--name", "MissingAdopter", "--destination", str(root), "--no-input",
                "--plugin-adopter", str(root / "missing.py"),
            )
            missing_input = self.run_cli(
                "new", "--name", "MissingInput", "--destination", str(root), "--no-input",
                "--plugin-adopter", str(self.standards_adopter), "--marketplace-revision", "invalid-revision",
            )

            self.assertEqual(2, missing_flags.returncode)
            self.assertEqual(1, missing_adopter.returncode)
            self.assertEqual(2, missing_input.returncode)
            self.assertFalse((root / "Missing").exists())
            self.assertFalse((root / "MissingAdopter").exists())
            self.assertFalse((root / "MissingInput").exists())

    def test_verify_callers_pass_required_standards_arguments_before_builds(self) -> None:
        class StopVerification(Exception):
            pass

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adopter = root / "adopt_repository.py"
            adopter.write_text("", encoding="utf-8")
            environment = {"PLUGIN_ADOPTER": str(adopter)}
            for caller in (
                lambda: VERIFY.verify("VerifyCaller", "minimal"),
                lambda: VERIFY.negative_path_gates("NegativeCaller", "web", ('tests=["integration"]',)),
                lambda: VERIFY.snippet_compile_gate("SnippetCaller"),
            ):
                with mock.patch.dict(os.environ, environment, clear=False):
                    with mock.patch.object(VERIFY, "run", side_effect=StopVerification) as run:
                        with self.assertRaises(StopVerification):
                            caller()
                command = run.call_args.args[0]
                self.assertEqual(str(adopter), command[command.index("--plugin-adopter") + 1])
                self.assertNotIn("--marketplace-revision", command)

    def test_verify_callers_reject_missing_standards_before_commands(self) -> None:
        for caller in (
            lambda: VERIFY.verify("VerifyMissing", "minimal"),
            lambda: VERIFY.negative_path_gates("NegativeMissing", "web"),
            lambda: VERIFY.snippet_compile_gate("SnippetMissing"),
        ):
            with mock.patch.dict(os.environ, {"PLUGIN_ADOPTER": ""}, clear=False):
                with mock.patch.object(VERIFY, "run") as run:
                    with self.assertRaises(RuntimeError):
                        caller()
            run.assert_not_called()

    def test_verify_main_uses_supported_azure_workflow_override(self) -> None:
        with (
            mock.patch.object(VERIFY, "verify") as verify,
            mock.patch.object(VERIFY, "snippet_compile_gate"),
            mock.patch.object(VERIFY, "negative_path_gates"),
        ):
            self.assertEqual(0, VERIFY.main())

        verify.assert_any_call("SandboxAzureSample", "sandbox", ("cloud=azure", "azure.workflows=false"), True)

    def test_documented_new_examples_execute_with_fixture_substitutions(self) -> None:
        standard_flags = (
            " --plugin-adopter <machine-plugin-selection-skill-directory>/scripts/adopt_plugins.py"
        )
        updated = SCAFFOLD_SKILL.read_text(encoding="utf-8")
        previous = updated.replace(standard_flags, "")
        self.assertNotEqual(updated, previous)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            azure_script = write_fake_azure(destination / "azure")
            previous_skill = destination / "previous-SKILL.md"
            updated_skill = destination / "updated-SKILL.md"
            previous_skill.write_text(previous, encoding="utf-8")
            updated_skill.write_text(updated, encoding="utf-8")
            replacements = (
                ("<skill-directory>/scripts/scaffold.py", SCRIPT.as_posix()),
                ("<machine-plugin-selection-skill-directory>/scripts/adopt_plugins.py", self.standards_adopter.as_posix()),
                ("~/source/repos/tj-agents/azure/.agents/azure/utility/scaffold/scripts/scaffold.py", azure_script.as_posix()),
                ("~/source/repos", destination.as_posix()),
            )
            def run_documented_commands(path: Path) -> list[subprocess.CompletedProcess[str]]:
                commands = re.findall(
                    r"^python -B <skill-directory>/scripts/scaffold\.py new .+$",
                    path.read_text(encoding="utf-8"),
                    flags=re.MULTILINE,
                )
                self.assertEqual(2, len(commands))
                results = []
                for command in commands:
                    rendered = command
                    for source, replacement in replacements:
                        rendered = rendered.replace(source, replacement)
                    arguments = shlex.split(rendered)
                    arguments[0] = sys.executable
                    results.append(subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, stdin=subprocess.PIPE))
                return results

            previous_results = run_documented_commands(previous_skill)
            for result in previous_results:
                self.assertEqual(2, result.returncode)
            self.assertFalse((destination / "MyService").exists())
            self.assertFalse((destination / "Sandbox").exists())

            updated_results = run_documented_commands(updated_skill)
            for result in updated_results:
                self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((destination / "MyService" / ".agents" / "plugins.json").is_file())
            self.assertTrue((destination / "Sandbox" / ".agents" / "plugins.json").is_file())
            self.assertTrue((destination / "Sandbox" / "infra" / "FAKE_AZURE_RAN.txt").is_file())

    def test_standards_adopter_receives_dotnet_and_azure_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log_path = root / "standards.log"
            env = dict(os.environ, FAKE_STANDARDS_LOG=str(log_path))
            standard = self.run_cli(
                "new", "--name", "Standard", "--destination", str(root), "--preset", "minimal", env=env,
            )
            azure = self.run_cli(
                "new", "--name", "Azure", "--destination", str(root), "--preset", "web", "--set", "cloud=azure", env=env,
            )

            self.assertEqual(0, standard.returncode, standard.stderr)
            self.assertEqual(0, azure.returncode, azure.stderr)
            calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(["write", "check", "write", "check"], [call[call.index("--mode") + 1] for call in calls])
            self.assertEqual(["dotnet", "dotnet", "azure", "azure"], [call[call.index("--stack") + 1] for call in calls])
            self.assertTrue(all("--marketplace-revision" not in call for call in calls))
            self.assertTrue(all([call[n + 1] for n, arg in enumerate(call) if arg == "--plugin"] == ["base@tj-agents", "engineering@tj-agents", "machine@tj-agents"] for call in calls))

    def test_standards_files_are_copied_and_listed_by_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            created = self.create(root, "Prepared", "minimal")
            preview = self.run_cli(
                "new", "--name", "Preview", "--destination", str(root), "--preset", "minimal", "--dry-run",
            )

            self.assertEqual(0, created.returncode, created.stderr)
            self.assertEqual(0, preview.returncode, preview.stderr)
            for relative in FAKE_STANDARD_FILES:
                self.assertTrue((root / "Prepared" / relative).is_file(), relative)
                self.assertIn(relative, json.loads(preview.stdout)["files"])
            self.assertFalse((root / "Preview").exists())

    def test_standards_adopter_failure_prevents_project_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.run_cli(
                "new", "--name", "Failure", "--destination", str(root), "--preset", "minimal",
                env=dict(os.environ, FAKE_STANDARDS_FAIL="1"),
            )

            self.assertEqual(1, result.returncode)
            self.assertFalse((root / "Failure").exists())

    def test_standards_adopter_check_failure_prevents_project_creation_and_dry_run_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log_path = root / "standards.log"
            env = dict(os.environ, FAKE_STANDARDS_CHECK_FAIL="1", FAKE_STANDARDS_LOG=str(log_path))
            created = self.run_cli(
                "new", "--name", "CheckFailure", "--destination", str(root), "--preset", "minimal", env=env,
            )
            preview = self.run_cli(
                "new", "--name", "CheckFailurePreview", "--destination", str(root), "--preset", "minimal", "--dry-run", env=env,
            )

            self.assertEqual(1, created.returncode)
            self.assertEqual(1, preview.returncode)
            self.assertFalse((root / "CheckFailure").exists())
            self.assertFalse((root / "CheckFailurePreview").exists())
            calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(["write", "check", "write", "check"], [call[call.index("--mode") + 1] for call in calls])

    def test_standards_required_outputs_and_selected_plugins_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing_output = self.run_cli(
                "new", "--name", "MissingOutput", "--destination", str(root), "--preset", "minimal",
                env=dict(os.environ, FAKE_STANDARDS_MISSING=".codex/config.toml"),
            )
            missing_plugin = self.run_cli(
                "new", "--name", "MissingPlugin", "--destination", str(root), "--preset", "minimal",
                env=dict(os.environ, FAKE_STANDARDS_OMIT_PLUGIN="dotnet@tj-agents"),
            )
            invalid_schema = self.run_cli(
                "new", "--name", "InvalidSchema", "--destination", str(root), "--preset", "minimal",
                env=dict(os.environ, FAKE_STANDARDS_SCHEMA_VERSION="3"),
            )

            pinned = self.run_cli(
                "new", "--name", "Pinned", "--destination", str(root), "--preset", "minimal",
                env=dict(os.environ, FAKE_STANDARDS_PIN="1"),
            )
            self.assertEqual(1, pinned.returncode)
            self.assertIn("without revision pins", pinned.stderr)
            self.assertFalse((root / "Pinned").exists())
            self.assertEqual(1, missing_output.returncode)
            self.assertEqual(1, missing_plugin.returncode)
            self.assertEqual(1, invalid_schema.returncode)
            self.assertIn("schema_version 1", invalid_schema.stderr)
            self.assertFalse((root / "MissingOutput").exists())
            self.assertFalse((root / "MissingPlugin").exists())
            self.assertFalse((root / "InvalidSchema").exists())

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
            result = self.create(root, "Example", "web")

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
                ".agents/skill-routes.json",
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
                "src/Example.Application/Example.Application.csproj",
                "src/Example.Domain/Example.Domain.csproj",
                "src/Example.Web/Example.Web.csproj",
                "src/Example.Web/Program.cs",
                "src/Example.Web/appsettings.json",
            ],
            "web": [
                ".agents/skill-routes.json",
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
                "src/Example.Application/Example.Application.csproj",
                "src/Example.Domain/Example.Domain.csproj",
                "src/Example.Infrastructure/Example.Infrastructure.csproj",
                "src/Example.Infrastructure/Persistence/ApplicationDbContext.cs",
                "src/Example.Infrastructure/ServiceCollectionExtensions.cs",
                "src/Example.Web/Example.Web.csproj",
                "src/Example.Web/Program.cs",
                "src/Example.Web/appsettings.json",
                "tests/Example.UnitTests/Example.UnitTests.csproj",
            ],
            "dapper-sqlserver": [
                ".agents/skill-routes.json",
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
                "src/Example.Application/Example.Application.csproj",
                "src/Example.Domain/Example.Domain.csproj",
                "src/Example.Infrastructure/DapperConnectionFactory.cs",
                "src/Example.Infrastructure/Example.Infrastructure.csproj",
                "src/Example.Infrastructure/IDapperConnectionFactory.cs",
                "src/Example.Infrastructure/ServiceCollectionExtensions.cs",
                "src/Example.Web/Example.Web.csproj",
                "src/Example.Web/Program.cs",
                "src/Example.Web/appsettings.json",
                "tests/Example.UnitTests/Example.UnitTests.csproj",
            ],
        }
        names = {"minimal": "Example", "web": "ExampleWeb", "dapper-sqlserver": "ExampleDapper"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for preset, expected_files in expected.items():
                name = names[preset]
                result = self.create(root, name, preset)

                self.assertEqual(0, result.returncode, result.stderr)
                generated = sorted(
                    path.relative_to(root / name).as_posix() for path in (root / name).rglob("*") if path.is_file()
                )
                rewritten = [item.replace("Example", name) for item in expected_files]
                self.assertEqual(sorted([*rewritten, *FAKE_STANDARD_FILES]), generated)

    def test_component_combinations_render_selected_wiring(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sql_server = self.create_with_options(root, "SqlServer", "web", "database=sqlserver")
            combined = self.create_with_options(
                root,
                "Combined",
                "web",
                "data=efcore+dapper",
                "auth=jwt",
                "telemetry=opentelemetry",
                "selected-stack=true",
            )

            self.assertEqual(0, sql_server.returncode, sql_server.stderr)
            self.assertEqual(0, combined.returncode, combined.stderr)
            self.assertIn(
                "UseSqlServer",
                (root / "SqlServer" / "src" / "SqlServer.Infrastructure" / "ServiceCollectionExtensions.cs").read_text(
                    encoding="utf-8"
                ),
            )
            combined_root = root / "Combined"
            program = (combined_root / "src" / "Combined.Web" / "Program.cs").read_text(encoding="utf-8")
            appsettings = json.loads((combined_root / "src" / "Combined.Web" / "appsettings.json").read_text(encoding="utf-8"))

            self.assertTrue((combined_root / "BannedSymbols.txt").is_file())
            self.assertIn("AddAuthentication", program)
            self.assertIn("AddOpenTelemetry", program)
            self.assertIn("DapperConnectionFactory.cs", {path.name for path in (combined_root / "src" / "Combined.Infrastructure").iterdir()})
            self.assertEqual("Combined", appsettings["Jwt"]["Audience"])

    def test_functions_only_and_worker_only_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            functions = self.create_with_options(root, "Functions", "minimal", 'hosts=["functions"]')
            worker = self.create_with_options(root, "Worker", "minimal", 'hosts=["worker"]')

            self.assertEqual(0, functions.returncode, functions.stderr)
            self.assertEqual(0, worker.returncode, worker.stderr)
            self.assertTrue((root / "Functions" / "src" / "Functions.Functions" / "Functions.Functions.csproj").is_file())
            self.assertFalse((root / "Functions" / "src" / "Functions.Web").exists())
            self.assertTrue((root / "Worker" / "src" / "Worker.Worker" / "Worker.Worker.csproj").is_file())
            self.assertFalse((root / "Worker" / "src" / "Worker.Web").exists())
    def test_host_and_integration_constraints_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            durable = self.create_with_options(root, "Durable", "minimal", 'hosts=["durable"]')
            integration_without_api = self.create_with_options(
                root,
                "IntegrationWithoutApi",
                "minimal",
                'hosts=["worker"]',
                'tests=["integration"]',
                "data=efcore",
                "database=postgres",
            )
            jwt_without_api = self.create_with_options(root, "JwtWithoutApi", "minimal", 'hosts=["worker"]', "auth=jwt")

            self.assertEqual(2, durable.returncode)
            self.assertEqual(2, integration_without_api.returncode)
            self.assertEqual(2, jwt_without_api.returncode)

    def test_sandbox_hosts_fixture_file_list(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create(root, "Sandbox", "sandbox")

            self.assertEqual(0, result.returncode, result.stderr)
            project = root / "Sandbox"
            generated = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())
            self.assertEqual(
                sorted([
                    ".agents/skill-routes.json",
                    ".editorconfig", ".gitattributes", ".github/workflows/ci.yml", ".gitignore", ".scaffold.json",
                    "AGENTS.md", "BannedSymbols.txt", "CLAUDE.md", "Directory.Build.props", "Directory.Packages.props",
                    "Sandbox.slnx", "global.json",
                    "src/Sandbox.Application/Sandbox.Application.csproj", "src/Sandbox.Domain/Sandbox.Domain.csproj",
                    "src/Sandbox.Functions/Program.cs", "src/Sandbox.Functions/Sandbox.Functions.csproj",
                    "src/Sandbox.Functions/host.json", "src/Sandbox.Functions/local.settings.json",
                    "src/Sandbox.Infrastructure/Persistence/ApplicationDbContext.cs",
                    "src/Sandbox.Infrastructure/Sandbox.Infrastructure.csproj", "src/Sandbox.Infrastructure/ServiceCollectionExtensions.cs",
                    "src/Sandbox.Web/Program.cs", "src/Sandbox.Web/Sandbox.Web.csproj", "src/Sandbox.Web/appsettings.json",
                    "src/Sandbox.Worker/Program.cs", "src/Sandbox.Worker/Sandbox.Worker.csproj", "src/Sandbox.Worker/appsettings.json",
                    "tests/Sandbox.IntegrationTests.Fixtures/ApiFixture.cs",
                    "tests/Sandbox.IntegrationTests.Fixtures/Sandbox.IntegrationTests.Fixtures.csproj",
                    "tests/Sandbox.IntegrationTests/BannedSymbols.txt",
                    "tests/Sandbox.IntegrationTests/Sandbox.IntegrationTests.csproj", "tests/Sandbox.UnitTests/Sandbox.UnitTests.csproj",
                    *FAKE_STANDARD_FILES,
                ]),
                generated,
            )
            functions = project / "src" / "Sandbox.Functions"
            fixture = project / "tests" / "Sandbox.IntegrationTests.Fixtures" / "ApiFixture.cs"
            self.assertIn("Microsoft.Azure.Functions.Worker.Extensions.DurableTask", (functions / "Sandbox.Functions.csproj").read_text(encoding="utf-8"))
            self.assertIn("UseFunctionsWorkerDefaults", (functions / "Program.cs").read_text(encoding="utf-8"))
            self.assertIn("telemetryMode", (functions / "host.json").read_text(encoding="utf-8"))
            self.assertIn("PostgreSqlContainer", fixture.read_text(encoding="utf-8"))
            fixture_content = fixture.read_text(encoding="utf-8")
            self.assertIn('new PostgreSqlBuilder("postgres:17.4")', fixture_content)
            self.assertIn("using System.Security.Cryptography;", fixture_content)
            self.assertIn("RandomNumberGenerator.GetBytes(24)", fixture_content)
            self.assertIn(".WithPassword(CreatePassword())", fixture_content)
            self.assertIn(".WithPortBinding(5432, true)", fixture_content)
            self.assertIn('"5432/tcp"][0].HostIP = "127.0.0.1"', fixture_content)
            self.assertNotIn("HeaderAuthenticationHandler", fixture.read_text(encoding="utf-8"))
            self.assertIn("local.settings.json", (project / ".gitignore").read_text(encoding="utf-8"))
            fixture_project = project / "tests" / "Sandbox.IntegrationTests.Fixtures" / "Sandbox.IntegrationTests.Fixtures.csproj"
            self.assertIn("<IsTestProject>false</IsTestProject>", fixture_project.read_text(encoding="utf-8"))
            packages = ElementTree.parse(project / "Directory.Packages.props").findall(".//PackageVersion")
            package_names = [package.attrib["Include"] for package in packages]
            self.assertEqual(len(package_names), len(set(package_names)))

    def test_sql_server_integration_jwt_renders_provider_and_auth_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(
                root,
                "SqlIntegration",
                "web",
                "database=sqlserver",
                'tests=["integration"]',
                "auth=jwt",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            fixture = (root / "SqlIntegration" / "tests" / "SqlIntegration.IntegrationTests.Fixtures" / "ApiFixture.cs").read_text(encoding="utf-8")

            self.assertIn("MsSqlContainer", fixture)
            self.assertIn('new MsSqlBuilder("mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")', fixture)
            self.assertIn("RandomNumberGenerator.GetBytes(24)", fixture)
            self.assertIn(".WithPassword(CreatePassword())", fixture)
            self.assertIn(".WithPortBinding(1433, true)", fixture)
            self.assertIn('"1433/tcp"][0].HostIP = "127.0.0.1"', fixture)
            self.assertIn("UseSqlServer(container.GetConnectionString())", fixture)
            self.assertIn("HeaderAuthenticationHandler", fixture)
            self.assertIn("X-Test-User", fixture)

    def test_hybrid_fixture_replaces_ef_and_dapper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "Hybrid", "web", "data=efcore+dapper", 'tests=["integration"]')

            self.assertEqual(0, result.returncode, result.stderr)
            fixture = (root / "Hybrid" / "tests" / "Hybrid.IntegrationTests.Fixtures" / "ApiFixture.cs").read_text(encoding="utf-8")

            self.assertIn("RemoveAll<DbContextOptions<ApplicationDbContext>>", fixture)
            self.assertIn("RemoveAll<IDapperConnectionFactory>()", fixture)
            self.assertIn("FixtureDapperConnectionFactory", fixture)
            self.assertIn(".WithPassword(CreatePassword())", fixture)
            self.assertIn('"5432/tcp"][0].HostIP = "127.0.0.1"', fixture)

    def test_integration_provider_package_versions_are_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dapper_postgres = self.create_with_options(root, "DapperPostgres", "web", "data=dapper", 'tests=["integration"]')
            hybrid_sql = self.create_with_options(root, "HybridSql", "web", "data=efcore+dapper", "database=sqlserver", 'tests=["integration"]')

            self.assertEqual(0, dapper_postgres.returncode, dapper_postgres.stderr)
            self.assertEqual(0, hybrid_sql.returncode, hybrid_sql.stderr)
            for name in ("DapperPostgres", "HybridSql"):
                packages = ElementTree.parse(root / name / "Directory.Packages.props").findall(".//PackageVersion")
                package_names = [package.attrib["Include"] for package in packages]
                self.assertEqual(len(package_names), len(set(package_names)))
                fixture = (root / name / "tests" / f"{name}.IntegrationTests.Fixtures" / "ApiFixture.cs").read_text(encoding="utf-8")
                self.assertIn("RandomNumberGenerator.GetBytes(24)", fixture)
                self.assertIn(".WithPassword(CreatePassword())", fixture)
                self.assertIn("HostIP = \"127.0.0.1\"", fixture)

    def test_sql_server_outputs_keep_certificate_validation_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ef_core = self.create_with_options(root, "EfCoreSqlServer", "web", "database=sqlserver")
            dapper = self.create(root, "DapperSqlServer", "dapper-sqlserver")

            self.assertEqual(0, ef_core.returncode, ef_core.stderr)
            self.assertEqual(0, dapper.returncode, dapper.stderr)
            for name in ("EfCoreSqlServer", "DapperSqlServer"):
                appsettings_path = root / name / "src" / f"{name}.Web" / "appsettings.json"
                appsettings = json.loads(appsettings_path.read_text(encoding="utf-8"))
                self.assertNotIn("TrustServerCertificate", appsettings["ConnectionStrings"]["SqlServer"])

    def test_cloud_azure_rejects_sqlserver(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "AzureSqlServer", "web", "cloud=azure", "database=sqlserver")

            self.assertEqual(2, result.returncode)
            self.assertFalse((root / "AzureSqlServer").exists())

    def test_azure_passthrough_requires_cloud_azure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "azure-config.json"
            config.write_text(json.dumps({"azure": {"key_vault": True}}), encoding="utf-8")

            via_set = self.create_with_options(root, "PassthroughSet", "web", "azure.http_host=app-service")
            via_config = self.run_cli(
                "new", "--name", "PassthroughConfig", "--destination", str(root), "--preset", "web",
                "--config", str(config),
            )

            self.assertEqual(2, via_set.returncode)
            self.assertEqual(2, via_config.returncode)
            self.assertFalse((root / "PassthroughSet").exists())
            self.assertFalse((root / "PassthroughConfig").exists())

    def test_azure_profile_content_for_web_and_sandbox_presets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            web_result = self.create_with_options(root, "WebAzure", "web", "cloud=azure")
            sandbox_result = self.create_with_options(root, "SandboxAzure", "sandbox", "cloud=azure")

            self.assertEqual(0, web_result.returncode, web_result.stderr)
            self.assertEqual(0, sandbox_result.returncode, sandbox_result.stderr)

            web_profile = json.loads((root / "WebAzure" / "infra" / "app.json").read_text(encoding="utf-8"))
            self.assertEqual(1, web_profile["schema_version"])
            self.assertEqual(["web"], [workload["id"] for workload in web_profile["workloads"]])
            web_workload = web_profile["workloads"][0]
            self.assertEqual("http", web_workload["kind"])
            self.assertEqual(8080, web_workload["port"])
            self.assertEqual("/health/live", web_workload["probes"]["liveness"])
            self.assertEqual("/health/ready", web_workload["probes"]["readiness"])
            self.assertIn("WebAzure.Web", web_workload["build"]["image"])
            self.assertIn("$REGISTRY", web_workload["build"]["image"])
            self.assertIn("WebAzure.Web", web_workload["build"]["package"])
            self.assertEqual({"name": "dotnet", "version": "10.0"}, web_workload["runtime"])
            self.assertEqual("webazure-web", web_workload["settings"]["OTEL_SERVICE_NAME"])
            self.assertEqual("postgres", web_profile["database"]["engine"])
            self.assertIn("efbundle", web_profile["database"]["migration"]["build"]["image"])
            self.assertEqual(["/efbundle"], web_profile["database"]["migration"]["command"])
            self.assertEqual(
                "Host={postgres.host};Database={postgres.database};Username={postgres.user};Ssl Mode=Require",
                web_profile["settings"]["ConnectionStrings__Postgres"],
            )
            self.assertEqual("{identity.client_id}", web_profile["settings"]["AZURE_CLIENT_ID"])
            self.assertNotIn("APPLICATIONINSIGHTS_CONNECTION_STRING", web_profile["settings"])

            sandbox_profile = json.loads((root / "SandboxAzure" / "infra" / "app.json").read_text(encoding="utf-8"))
            ids = [workload["id"] for workload in sandbox_profile["workloads"]]
            self.assertEqual(["web", "worker", "functions"], ids)
            functions_workload = sandbox_profile["workloads"][2]
            self.assertEqual("functions", functions_workload["kind"])
            self.assertEqual({"name": "dotnet-isolated", "version": "10.0"}, functions_workload["runtime"])
            self.assertIn("image", functions_workload["build"])
            self.assertIn("package", functions_workload["build"])
            self.assertEqual(
                "{monitor.connection_string}", sandbox_profile["settings"]["APPLICATIONINSIGHTS_CONNECTION_STRING"]
            )

    def test_azure_cloud_container_support_on_worker_and_functions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "SandboxAzure", "sandbox", "cloud=azure")

            self.assertEqual(0, result.returncode, result.stderr)
            project = root / "SandboxAzure"
            worker_csproj = (project / "src" / "SandboxAzure.Worker" / "SandboxAzure.Worker.csproj").read_text(encoding="utf-8")
            functions_csproj = (project / "src" / "SandboxAzure.Functions" / "SandboxAzure.Functions.csproj").read_text(encoding="utf-8")

            self.assertIn("<EnableSdkContainerSupport>true</EnableSdkContainerSupport>", worker_csproj)
            self.assertNotIn("ContainerBaseImage", worker_csproj)
            self.assertIn("<EnableSdkContainerSupport>true</EnableSdkContainerSupport>", functions_csproj)
            self.assertIn(
                "<ContainerBaseImage>mcr.microsoft.com/azure-functions/dotnet-isolated:4-dotnet-isolated10.0</ContainerBaseImage>",
                functions_csproj,
            )

    def test_azure_telemetry_usings_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "SandboxAzureTelemetry", "sandbox", "cloud=azure")

            self.assertEqual(0, result.returncode, result.stderr)
            project = root / "SandboxAzureTelemetry"
            web_program = (project / "src" / "SandboxAzureTelemetry.Web" / "Program.cs").read_text(encoding="utf-8")
            worker_program = (project / "src" / "SandboxAzureTelemetry.Worker" / "Program.cs").read_text(encoding="utf-8")
            functions_program = (project / "src" / "SandboxAzureTelemetry.Functions" / "Program.cs").read_text(encoding="utf-8")

            self.assertIn("using Azure.Monitor.OpenTelemetry.AspNetCore;", web_program)
            self.assertIn("using Azure.Monitor.OpenTelemetry.Exporter;", worker_program)
            self.assertIn("using Azure.Monitor.OpenTelemetry.Exporter;", functions_program)

    def test_azure_web_postgres_ef_emits_a_single_add_health_checks_call(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "AzureHealthChecks", "web", "cloud=azure")

            self.assertEqual(0, result.returncode, result.stderr)
            program = (root / "AzureHealthChecks" / "src" / "AzureHealthChecks.Web" / "Program.cs").read_text(encoding="utf-8")

            self.assertEqual(1, program.count("AddHealthChecks()"))
            self.assertIn("var healthChecks = builder.Services.AddHealthChecks();", program)
            self.assertIn('healthChecks.AddDbContextCheck<ApplicationDbContext>("database");', program)

    def test_cloud_name_derivation_and_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            derived = self.create_with_options(root, "ExampleWeb", "web", "cloud=azure")
            overridden = self.create_with_options(root, "ExampleWeb2", "web", "cloud=azure", "cloud-name=myappname")
            invalid = self.create_with_options(root, "123Invalid", "web", "cloud=azure")

            self.assertEqual(0, derived.returncode, derived.stderr)
            self.assertEqual(0, overridden.returncode, overridden.stderr)
            self.assertEqual(2, invalid.returncode)
            self.assertFalse((root / "123Invalid").exists())

            derived_profile = json.loads((root / "ExampleWeb" / "infra" / "app.json").read_text(encoding="utf-8"))
            overridden_profile = json.loads((root / "ExampleWeb2" / "infra" / "app.json").read_text(encoding="utf-8"))
            self.assertEqual("exampleweb", derived_profile["name"])
            self.assertEqual("myappname", overridden_profile["name"])

    def test_prompt_value_reprompts_on_invalid_input(self) -> None:
        definition = {"type": "string", "allowed": ["a", "b"], "default": "a"}
        answers = iter(["z", "b"])

        result = SCAFFOLD.prompt_value("option", definition, lambda prompt: next(answers))

        self.assertEqual("b", result)

    def test_prompt_value_empty_answer_keeps_default(self) -> None:
        definition = {"type": "string", "allowed": ["a", "b"], "default": "a"}

        result = SCAFFOLD.prompt_value("option", definition, lambda prompt: "")

        self.assertEqual("a", result)

    def test_interactive_options_skips_already_set_values(self) -> None:
        option_schema = SCAFFOLD.schema()
        resolved = {key: definition["default"] for key, definition in option_schema.items()}
        sources = {key: "options.json" for key in option_schema}
        sources["cloud"] = "--set"
        resolved["cloud"] = "azure"
        answers = {key: "" for key in option_schema if key != "cloud"}
        answers["cloud-name"] = "myapp"

        def fake_input(prompt: str) -> str:
            key = prompt.split(" (")[0].split(" [")[0]
            return answers[key]

        updated = SCAFFOLD.interactive_options(option_schema, resolved, sources, fake_input)

        self.assertEqual("azure", updated["cloud"])
        self.assertEqual("myapp", updated["cloud-name"])
        self.assertEqual("postgres", updated["database"])

    def test_interactive_azure_options_prompts_unset_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            azure_script = write_fake_azure(Path(temporary) / "azure")
            answers = {"http_host": "app-service", "key_vault": "true"}

            def fake_input(prompt: str) -> str:
                key = prompt.split(" (")[0].split(" [")[0]
                return answers[key]

            updated = SCAFFOLD.interactive_azure_options(azure_script, {}, fake_input)

            self.assertEqual("app-service", updated["http_host"])
            self.assertEqual("true", updated["key_vault"])

    def test_azure_invocation_dry_run_failure_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            azure_script = write_fake_azure(root / "azure")
            env = dict(os.environ, FAKE_AZURE_FAIL="dry")

            result = subprocess.run(
                [
                    sys.executable, "-B", str(SCRIPT), "new", "--name", "AzureDryFail", "--destination", str(root),
                    "--preset", "web", "--set", "cloud=azure", "--azure-scaffold", str(azure_script), "--no-input",
                    *self.standards_arguments(),
                ],
                cwd=ROOT, capture_output=True, text=True, env=env,
            )

            self.assertEqual(2, result.returncode, result.stderr)
            self.assertFalse((root / "AzureDryFail").exists())

    def test_azure_invocation_real_run_failure_keeps_dotnet_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            azure_script = write_fake_azure(root / "azure")
            env = dict(os.environ, FAKE_AZURE_FAIL="real")

            result = subprocess.run(
                [
                    sys.executable, "-B", str(SCRIPT), "new", "--name", "AzureRealFail", "--destination", str(root),
                    "--preset", "web", "--set", "cloud=azure", "--azure-scaffold", str(azure_script), "--no-input",
                    *self.standards_arguments(),
                ],
                cwd=ROOT, capture_output=True, text=True, env=env,
            )

            self.assertEqual(1, result.returncode, result.stderr)
            self.assertTrue((root / "AzureRealFail" / "infra" / "app.json").is_file())
            self.assertFalse((root / "AzureRealFail" / "infra" / "FAKE_AZURE_RAN.txt").exists())

    def test_azure_invocation_success_runs_dry_then_real_and_records_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            azure_script = write_fake_azure(root / "azure")
            log_path = root / "fake-azure.log"
            env = dict(os.environ, FAKE_AZURE_LOG=str(log_path))

            result = subprocess.run(
                [
                    sys.executable, "-B", str(SCRIPT), "new", "--name", "AzureOk", "--destination", str(root),
                    "--preset", "web", "--set", "cloud=azure", "--set", "azure.http_host=app-service",
                    "--azure-scaffold", str(azure_script), "--no-input", *self.standards_arguments(),
                ],
                cwd=ROOT, capture_output=True, text=True, env=env,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            project = root / "AzureOk"
            self.assertTrue((project / "infra" / "FAKE_AZURE_RAN.txt").is_file())
            self.assertEqual("name: Azure CI\n", (project / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
            metadata = json.loads((project / ".scaffold.json").read_text(encoding="utf-8"))
            self.assertEqual({"http_host": "app-service"}, metadata["azure"])
            calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(calls))
            dry_call, real_call = calls
            self.assertIn("--dry-run", dry_call)
            self.assertNotIn(str(project), dry_call)
            self.assertNotIn("--dry-run", real_call)
            self.assertIn(str(project), real_call)

    def test_missing_azure_path_prints_command_and_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "NoAzurePath", "web", "cloud=azure")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("new --into", result.stdout)
            self.assertIn(str(root / "NoAzurePath"), result.stdout)
            self.assertTrue((root / "NoAzurePath" / "infra" / "app.json").is_file())
            self.assertFalse((root / "NoAzurePath" / ".github" / "workflows" / "ci.yml").exists())

    def test_azure_command_line_quotes_values_with_spaces(self) -> None:
        line = SCAFFOLD.azure_command_line(
            "C:/Program Files/azure/scaffold.py", Path("C:/tmp/My Project"), {"topics": "a b"}
        )

        self.assertIn('"C:/Program Files/azure/scaffold.py"', line)
        self.assertIn('--set "topics=a b"', line)

    def test_azure_command_line_escapes_embedded_quotes(self) -> None:
        line = SCAFFOLD.azure_command_line("scaffold.py", Path("project"), {"key": 'va"lue'})

        self.assertIn('"key=va\\"lue"', line)

    def test_azure_command_line_doubles_a_trailing_backslash(self) -> None:
        line = SCAFFOLD.azure_command_line("scaffold.py", Path("project"), {"root": "C:\\"})

        self.assertIn('"root=C:\\\\"', line)

    def test_azure_command_line_escapes_a_backslash_before_a_quote(self) -> None:
        line = SCAFFOLD.azure_command_line("scaffold.py", Path("project"), {"key": 'a\\"'})

        self.assertIn('"key=a\\\\\\""', line)

    def test_azure_command_line_keeps_interior_backslashes_single(self) -> None:
        line = SCAFFOLD.azure_command_line("scaffold.py", Path("project"), {"path": "C:\\Program Files\\x"})

        self.assertIn('"path=C:\\Program Files\\x"', line)

    def test_cloud_none_output_has_no_azure_markers_or_unresolved_tokens(self) -> None:
        markers = (
            "Azure.Identity",
            "Azure.Monitor",
            "UseAzureMonitor",
            "AddAzureMonitorTraceExporter",
            "UsePeriodicPasswordProvider",
            "/health/live",
            "/health/ready",
            "EnableSdkContainerSupport",
            "ContainerBaseImage",
            "Microsoft.EntityFrameworkCore.Design",
        )
        cases = (
            ("minimal", "Example"),
            ("web", "ExampleWeb"),
            ("dapper-sqlserver", "ExampleDapper"),
            ("sandbox", "Sandbox"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for preset, name in cases:
                result = self.create(root, name, preset)

                self.assertEqual(0, result.returncode, result.stderr)
                project = root / name
                self.assertFalse((project / "infra").exists(), preset)
                self.assertFalse((project / ".config" / "dotnet-tools.json").exists(), preset)
                for path in project.rglob("*"):
                    if not path.is_file():
                        continue
                    text = path.read_text(encoding="utf-8")
                    for marker in markers:
                        self.assertNotIn(marker, text, f"{preset}:{path.relative_to(project).as_posix()} contains {marker}")
                    unresolved = re.search(r"\$[A-Z][A-Z0-9_]*\$", text)
                    self.assertIsNone(unresolved, f"{preset}:{path.relative_to(project).as_posix()} has {unresolved}")

    def test_azure_components_are_gated_on_cloud_azure(self) -> None:
        azure_components = [name for name, _, _ in SCAFFOLD.component_manifests() if name.startswith("azure")]

        self.assertTrue(azure_components)
        for name, manifest, _ in SCAFFOLD.component_manifests():
            if name not in azure_components:
                continue
            self.assertEqual("azure", manifest.get("when", {}).get("cloud"), f"component {name} when: {manifest.get('when')}")

    def test_generated_repo_carries_the_skill_route_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create(root, "Routed", "web")

            self.assertEqual(0, result.returncode, result.stderr)
            routes_path = root / "Routed" / ".agents" / "skill-routes.json"
            self.assertTrue(routes_path.is_file())
            table = json.loads(routes_path.read_text(encoding="utf-8"))
            self.assertEqual(SCAFFOLD.skill_routes_document(), table)
            routes_module_spec = importlib.util.spec_from_file_location(
                "dotnet_gen_skill_routes", SCRIPT.parent.parent.parent / "skill-routes" / "scripts" / "gen_skill_routes.py"
            )
            routes_module = importlib.util.module_from_spec(routes_module_spec)
            routes_module_spec.loader.exec_module(routes_module)
            for path, skill in (
                ("tests/Routed.UnitTests/FooTests.cs", "dotnet:testing-unit"),
                ("tests/Routed.IntegrationTests/FooApiTests.cs", "dotnet:testing-integration"),
                ("tests/Routed.E2ETests/Foo.feature", "dotnet:testing-e2e"),
            ):
                matched = routes_module.skills_for("dotnet-service", path)
                self.assertIn("dotnet:testing", matched)
                self.assertIn(skill, matched)


if __name__ == "__main__":
    unittest.main()
