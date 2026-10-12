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
from xml.etree import ElementTree


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
                "new", "--name", "Example", "--destination", str(root), "--set", "hosts=[api,api]"
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
        api = (
            "api",
            SCAFFOLD.read_json(SCAFFOLD.COMPONENTS / "api" / "component.json", "component api"),
            SCAFFOLD.COMPONENTS / "api",
        )
        appended = [
            api,
            ("first", {"append": {"API_USINGS": "using First;"}, "projects": []}, ROOT),
            ("second", {"append": {"API_USINGS": "using Second;"}, "projects": []}, ROOT),
        ]
        collisions = [
            ("first", {"variables": {"OWNER": "first"}, "projects": []}, ROOT),
            ("second", {"variables": {"OWNER": "second"}, "projects": []}, ROOT),
        ]

        with mock.patch.object(SCAFFOLD, "selected_components", return_value=appended):
            files = SCAFFOLD.plan("Example", options, None)

        self.assertIn("using First;\nusing Second;", files["src/Example.Api/Program.cs"])
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
            "dapper-sqlserver": [
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
                "src/Example.Infrastructure/DapperConnectionFactory.cs",
                "src/Example.Infrastructure/Example.Infrastructure.csproj",
                "src/Example.Infrastructure/IDapperConnectionFactory.cs",
                "src/Example.Infrastructure/ServiceCollectionExtensions.cs",
                "tests/Example.UnitTests/Example.UnitTests.csproj",
            ],
        }
        names = {"minimal": "Example", "api": "ExampleApi", "dapper-sqlserver": "ExampleDapper"}
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
                self.assertEqual(rewritten, generated)

    def test_component_combinations_render_selected_wiring(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sql_server = self.create_with_options(root, "SqlServer", "api", "database=sqlserver")
            combined = self.create_with_options(
                root,
                "Combined",
                "api",
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
            program = (combined_root / "src" / "Combined.Api" / "Program.cs").read_text(encoding="utf-8")
            appsettings = json.loads((combined_root / "src" / "Combined.Api" / "appsettings.json").read_text(encoding="utf-8"))

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
            self.assertFalse((root / "Functions" / "src" / "Functions.Api").exists())
            self.assertTrue((root / "Worker" / "src" / "Worker.Worker" / "Worker.Worker.csproj").is_file())
            self.assertFalse((root / "Worker" / "src" / "Worker.Api").exists())
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
                [
                    ".editorconfig", ".gitattributes", ".github/workflows/ci.yml", ".gitignore", ".scaffold.json",
                    "AGENTS.md", "BannedSymbols.txt", "CLAUDE.md", "Directory.Build.props", "Directory.Packages.props",
                    "Sandbox.slnx", "global.json", "src/Sandbox.Api/Program.cs", "src/Sandbox.Api/Sandbox.Api.csproj",
                    "src/Sandbox.Api/appsettings.json", "src/Sandbox.Core/Sandbox.Core.csproj",
                    "src/Sandbox.Functions/Program.cs", "src/Sandbox.Functions/Sandbox.Functions.csproj",
                    "src/Sandbox.Functions/host.json", "src/Sandbox.Functions/local.settings.json",
                    "src/Sandbox.Infrastructure/Persistence/ApplicationDbContext.cs",
                    "src/Sandbox.Infrastructure/Sandbox.Infrastructure.csproj", "src/Sandbox.Infrastructure/ServiceCollectionExtensions.cs",
                    "src/Sandbox.Worker/Program.cs", "src/Sandbox.Worker/Sandbox.Worker.csproj", "src/Sandbox.Worker/appsettings.json",
                    "tests/Sandbox.IntegrationTests.Fixtures/ApiFixture.cs",
                    "tests/Sandbox.IntegrationTests.Fixtures/Sandbox.IntegrationTests.Fixtures.csproj",
                    "tests/Sandbox.IntegrationTests/Sandbox.IntegrationTests.csproj", "tests/Sandbox.UnitTests/Sandbox.UnitTests.csproj",
                ],
                generated,
            )
            functions = project / "src" / "Sandbox.Functions"
            fixture = project / "tests" / "Sandbox.IntegrationTests.Fixtures" / "ApiFixture.cs"
            self.assertIn("Microsoft.Azure.Functions.Worker.Extensions.DurableTask", (functions / "Sandbox.Functions.csproj").read_text(encoding="utf-8"))
            self.assertIn("UseFunctionsWorkerDefaults", (functions / "Program.cs").read_text(encoding="utf-8"))
            self.assertIn("telemetryMode", (functions / "host.json").read_text(encoding="utf-8"))
            self.assertIn("PostgreSqlContainer", fixture.read_text(encoding="utf-8"))
            self.assertIn('new PostgreSqlBuilder("postgres:17.4")', fixture.read_text(encoding="utf-8"))
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
                "api",
                "database=sqlserver",
                'tests=["integration"]',
                "auth=jwt",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            fixture = (root / "SqlIntegration" / "tests" / "SqlIntegration.IntegrationTests.Fixtures" / "ApiFixture.cs").read_text(encoding="utf-8")

            self.assertIn("MsSqlContainer", fixture)
            self.assertIn('new MsSqlBuilder("mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")', fixture)
            self.assertIn("UseSqlServer(this.container.GetConnectionString())", fixture)
            self.assertIn("HeaderAuthenticationHandler", fixture)
            self.assertIn("X-Test-User", fixture)

    def test_hybrid_fixture_replaces_ef_and_dapper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self.create_with_options(root, "Hybrid", "api", "data=efcore+dapper", 'tests=["integration"]')

            self.assertEqual(0, result.returncode, result.stderr)
            fixture = (root / "Hybrid" / "tests" / "Hybrid.IntegrationTests.Fixtures" / "ApiFixture.cs").read_text(encoding="utf-8")

            self.assertIn("RemoveAll<DbContextOptions<ApplicationDbContext>>", fixture)
            self.assertIn("RemoveAll<IDapperConnectionFactory>()", fixture)
            self.assertIn("FixtureDapperConnectionFactory", fixture)

    def test_integration_provider_package_versions_are_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dapper_postgres = self.create_with_options(root, "DapperPostgres", "api", "data=dapper", 'tests=["integration"]')
            hybrid_sql = self.create_with_options(root, "HybridSql", "api", "data=efcore+dapper", "database=sqlserver", 'tests=["integration"]')

            self.assertEqual(0, dapper_postgres.returncode, dapper_postgres.stderr)
            self.assertEqual(0, hybrid_sql.returncode, hybrid_sql.stderr)
            for name in ("DapperPostgres", "HybridSql"):
                packages = ElementTree.parse(root / name / "Directory.Packages.props").findall(".//PackageVersion")
                package_names = [package.attrib["Include"] for package in packages]
                self.assertEqual(len(package_names), len(set(package_names)))

    def test_sql_server_outputs_keep_certificate_validation_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ef_core = self.create_with_options(root, "EfCoreSqlServer", "api", "database=sqlserver")
            dapper = self.create(root, "DapperSqlServer", "dapper-sqlserver")

            self.assertEqual(0, ef_core.returncode, ef_core.stderr)
            self.assertEqual(0, dapper.returncode, dapper.stderr)
            for name in ("EfCoreSqlServer", "DapperSqlServer"):
                appsettings_path = root / name / "src" / f"{name}.Api" / "appsettings.json"
                appsettings = json.loads(appsettings_path.read_text(encoding="utf-8"))
                self.assertNotIn("TrustServerCertificate", appsettings["ConnectionStrings"]["SqlServer"])


if __name__ == "__main__":
    unittest.main()
