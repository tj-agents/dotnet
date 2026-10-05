from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / ".agents/dotnet/utility/skill-routes/scripts/gen_skill_routes.py"
CORE_ROOTS = (ROOT / ".core", ROOT.parent / "core", ROOT.parent.parent.parent / "core")


def load(name: str, path: Path):
    loader = SourceFileLoader(name, str(path))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(module)
    return module


def core_root() -> Path | None:
    for root in CORE_ROOTS:
        if (root / "plugins/base/hooks/skill_router.py").is_file():
            return root
    return None


generator = load("dotnet_gen_skill_routes", GENERATOR)

TEST_CSPROJ = '<Project Sdk="Microsoft.NET.Sdk"><ItemGroup><PackageReference Include="Microsoft.NET.Test.Sdk" /></ItemGroup></Project>'

CARVED_TREE = {
    ("api/src/Acme.Authz.Api/Placeholder/PlaceholderEndpoints.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:http-api"},
    ("api/src/Acme.Authz.Api/Placeholder/PlaceholderResponse.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:naming-dtos"},
    ("api/src/Acme.Authz.Api/Grants/ServiceCollectionExtensions.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:dependency-injection"},
    ("api/src/Acme.Authz.Api/Program.cs", "var builder = WebApplication.CreateBuilder(args);"): {"dotnet:style", "dotnet:naming", "dotnet:dependency-injection"},
    ("api/src/Acme.Authz.Domain/SystemClock.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:domain-design"},
    ("api/src/Acme.Authz.Contracts/PermissionCheck.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:naming-dtos"},
    ("api/src/Acme.Authz.Api/Persistence/MigrationRunner.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:persistence"},
    ("api/test/Acme.Authz.Api.Tests.Integration/ApiFixture.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:testing", "dotnet:testing-integration"},
    ("api/test/Acme.Authz.Api.Tests.Unit/TelemetryTestEnvironment.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:testing", "dotnet:testing-unit"},
    ("api/test/Acme.Authz.Tests.Builders/AccessGrantBuilder.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:testing"},
    ("api/src/Acme.Authz.Api/Acme.Authz.Api.csproj", '<Project Sdk="Microsoft.NET.Sdk.Web"></Project>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure"},
    ("api/test/Acme.Authz.Api.Tests.Unit/Acme.Authz.Api.Tests.Unit.csproj", TEST_CSPROJ): {"dotnet:build", "dotnet:libraries", "dotnet:structure", "dotnet:testing", "dotnet:testing-unit"},
    ("api/test/Acme.Authz.Tests.E2E/Features/AccessReview.feature", ""): {"dotnet:testing", "dotnet:testing-e2e"},
    ("features/AccessReview.feature", ""): {"dotnet:testing", "dotnet:testing-e2e"},
    ("api/src/Acme.Authz.Api/Telemetry/Log.cs", "[LoggerMessage(Level = LogLevel.Information)]"): {"dotnet:style", "dotnet:naming", "dotnet:logging"},
    ("api/src/Acme.Authz.Api/Grants/GrantStore.cs", "private readonly ILoggerFactory loggerFactory;"): {"dotnet:style", "dotnet:naming", "dotnet:logging"},
    ("api/src/Acme.Authz.Application/Access/RequestAccess.cs", "public Result<AccessGrant, RequestAccessError> Handle()"): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:errors"},
    ("api/src/Acme.Authz.Api/CLAUDE.md", ""): {"engineering:docs-and-debt"},
    ("src/Acme.Billing.Infrastructure/Repositories/InvoiceRepository.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:persistence", "dotnet:naming-repositories"},
    ("src/Acme.Billing.Application/Invoices/RegisterInvoiceHandler.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules"},
    ("src/Acme.Billing.Infrastructure/BillingDbContext.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:persistence"},
    ("src/Acme.Billing.Infrastructure/Migrations/20260101000000_Init.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:persistence"},
    ("src/Acme.Billing.Api/Invoices/InvoiceMappers.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:naming-mapping"},
    ("src/Acme.Billing.Application/Invoices/RegisterInvoiceValidator.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:validation"},
    ("src/Acme.Billing.Infrastructure/Seeding/InvoiceSeeder.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:structure-modules", "dotnet:seeding"},
    ("proto/authz/v1/authz.proto", ""): {"dotnet:proto"},
    ("plans/skill-routes/PLAN.md", ""): {"engineering:plans"},
    ("reviews/Feature-SkillRoutes/REVIEW.md", ""): {"engineering:review-lifecycle"},
    ("AGENTS.md", ""): {"engineering:docs-and-debt"},
    ("TECH_DEBT.md", ""): {"engineering:docs-and-debt"},
    ("db/migrations/0001_init.sql", ""): set(),
    ("model/authorization-model.fga", ""): set(),
    (".github/workflows/ci.yml", ""): set(),
}


class RouteDerivationTests(unittest.TestCase):
    def test_carved_tree_resolves_expected_skills(self) -> None:
        for (path, content), expected in CARVED_TREE.items():
            with self.subTest(path=path):
                self.assertEqual(expected, generator.skills_for("dotnet-service", path, content))

    def test_matching_agrees_with_the_shipped_router(self) -> None:
        root = core_root()
        if root is None:
            self.skipTest("no core checkout visible to load the shipped router")
        hooks = root / "plugins/base/hooks"
        sys.path.insert(0, str(hooks))
        try:
            router = load("core_skill_router", hooks / "skill_router.py")
        finally:
            sys.path.remove(str(hooks))
        routes = generator.routes("dotnet-service")["routes"]
        for (path, content), expected in CARVED_TREE.items():
            with self.subTest(path=path):
                matched = {
                    skill
                    for route in router.matching_routes(routes, path, content)
                    for skill in route.get("skills") or []
                }
                self.assertEqual(expected, matched)

    def test_every_csharp_file_hits_the_floor(self) -> None:
        for (path, content), _ in CARVED_TREE.items():
            if not path.endswith(".cs"):
                continue
            with self.subTest(path=path):
                matched = generator.skills_for("dotnet-service", path, content)
                self.assertLessEqual({"dotnet:style", "dotnet:naming"}, matched)

    def test_rows_port_between_monorepo_and_carved_layouts(self) -> None:
        for (path, content), expected in CARVED_TREE.items():
            if not path.startswith("api/"):
                continue
            with self.subTest(path=path):
                self.assertEqual(expected, generator.skills_for("dotnet-service", path[len("api/"):], content))

    def test_no_row_is_dead_on_the_simulated_tree(self) -> None:
        for index, route in enumerate(generator.routes("dotnet-service")["routes"]):
            needle = route.get("content_requires")
            fired = any(
                re.search(route["path"], path) and (not needle or re.search(needle, content))
                for (path, content) in CARVED_TREE
            )
            self.assertTrue(fired, f"route {index} ({route['path']}) matches nothing in the simulated tree")

    def test_route_path_strings_are_pairwise_distinct(self) -> None:
        paths = [route["path"] for route in generator.routes("dotnet-service")["routes"]]
        self.assertEqual(len(paths), len(set(paths)), "skill_router keys seen-state on the path string")

    def test_routed_skills_resolve_and_stay_inside_the_layers(self) -> None:
        declaration = generator.routes("dotnet-service")
        root = core_root()
        for route in declaration["routes"]:
            for identifier in route["skills"]:
                package, capability = identifier.split(":")
                self.assertIn(package, declaration["layers"])
                if package == "dotnet":
                    self.assertTrue((ROOT / "plugins" / package / "skills" / capability / "SKILL.md").is_file(), identifier)
                else:
                    if root is None:
                        self.skipTest("no core checkout visible to verify engineering skills")
                    self.assertTrue((root / "plugins" / package / "skills" / capability / "SKILL.md").is_file(), identifier)

    def test_registry_names_known_kinds_and_lowercase_identities(self) -> None:
        document = generator.registry_document()
        self.assertEqual(sorted(generator.REGISTRY), list(document["repos"]))
        self.assertTrue(document["repos"])
        for identity, kind in document["repos"].items():
            self.assertRegex(identity, r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$")
            self.assertIn(kind, generator.KINDS)


class RouteCliTests(unittest.TestCase):
    @staticmethod
    def run_generator(*arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(GENERATOR), *arguments],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_kind_into_writes_a_current_consumer_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            written = self.run_generator("--kind", "dotnet-service", "--into", str(root))
            self.assertEqual(0, written.returncode, written.stdout + written.stderr)
            table = json.loads((root / ".agents/skill-routes.json").read_text(encoding="utf-8"))
            self.assertEqual(generator.routes("dotnet-service"), table)
            current = self.run_generator("--kind", "dotnet-service", "--into", str(root), "--check")
            self.assertEqual(0, current.returncode, current.stdout + current.stderr)
            (root / ".agents/skill-routes.json").write_text("{}", encoding="utf-8")
            stale = self.run_generator("--kind", "dotnet-service", "--into", str(root), "--check")
            self.assertEqual(1, stale.returncode)
            self.assertIn("STALE", stale.stdout)

    def test_emit_registry_writes_the_registry_and_each_kind_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            routes_dir = Path(temporary) / "routes"
            written = self.run_generator("--emit-registry", str(routes_dir))
            self.assertEqual(0, written.returncode, written.stdout + written.stderr)
            registry = json.loads((routes_dir / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(generator.registry_document(), registry)
            for kind in set(generator.REGISTRY.values()):
                table = json.loads((routes_dir / f"{kind}.json").read_text(encoding="utf-8"))
                self.assertEqual(generator.routes(kind), table)
            current = self.run_generator("--emit-registry", str(routes_dir), "--check")
            self.assertEqual(0, current.returncode, current.stdout + current.stderr)
            (routes_dir / "registry.json").write_text("{}", encoding="utf-8")
            stale = self.run_generator("--emit-registry", str(routes_dir), "--check")
            self.assertEqual(1, stale.returncode)
            self.assertIn("STALE", stale.stdout)

    def test_emit_registry_cannot_be_combined_with_kind(self) -> None:
        result = self.run_generator("--emit-registry", "routes", "--kind", "dotnet-service", "--into", ".")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot be combined", result.stderr)

    def test_kind_requires_into(self) -> None:
        result = self.run_generator("--kind", "dotnet-service")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--kind and --into are required", result.stderr)

    def test_unknown_kind_is_rejected(self) -> None:
        result = self.run_generator("--kind", "react-app", "--into", ".")
        self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
