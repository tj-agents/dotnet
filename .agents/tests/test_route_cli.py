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
    ("api/src/Acme.Authz.Api/Placeholder/PlaceholderEndpoints.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:http-api"},
    ("api/src/Acme.Authz.Api/Placeholder/PlaceholderResponse.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:naming-dtos"},
    ("api/src/Acme.Authz.Api/Grants/ServiceCollectionExtensions.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:dependency-injection", "dotnet:mapping"},
    ("api/src/Acme.Authz.Api/Program.cs", "var builder = WebApplication.CreateBuilder(args);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:dependency-injection"},
    ("api/src/Acme.Authz.Domain/SystemClock.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design"},
    ("api/src/Acme.Authz.Contracts/PermissionCheck.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:naming-dtos"},
    ("api/src/Acme.Authz.Api/Persistence/MigrationRunner.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "efcore:persistence"},
    ("api/test/Acme.Authz.Api.Tests.Integration/ApiFixture.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:testing", "dotnet:testing-integration"},
    ("api/test/Acme.Authz.Api.Tests.Unit/TelemetryTestEnvironment.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:testing", "dotnet:testing-unit"},
    ("api/test/Acme.Authz.Tests.Builders/AccessGrantBuilder.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:testing"},
    ("api/src/Acme.Authz.Api/Acme.Authz.Api.csproj", '<Project Sdk="Microsoft.NET.Sdk.Web"></Project>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure"},
    ("api/test/Acme.Authz.Api.Tests.Unit/Acme.Authz.Api.Tests.Unit.csproj", TEST_CSPROJ): {"dotnet:build", "dotnet:libraries", "dotnet:structure", "dotnet:testing", "dotnet:testing-unit"},
    ("api/test/Acme.Authz.Tests.E2E/Features/AccessReview.feature", ""): {"dotnet:testing", "dotnet:testing-e2e"},
    ("features/AccessReview.feature", ""): {"dotnet:testing", "dotnet:testing-e2e"},
    ("api/src/Acme.Authz.Api/Telemetry/Log.cs", "[LoggerMessage(Level = LogLevel.Information)]"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:logging"},
    ("api/src/Acme.Authz.Api/Grants/GrantStore.cs", "private readonly ILoggerFactory loggerFactory;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:logging"},
    ("api/src/Acme.Authz.Application/Access/RequestAccess.cs", "public Result<AccessGrant, RequestAccessError> Handle()"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:errors", "dotnet:errors-carriers"},
    ("api/src/Acme.Authz.Api/CLAUDE.md", ""): {"engineering:docs"},
    ("src/Acme.Billing.Infrastructure/Repositories/InvoiceRepository.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:repositories"},
    ("src/Acme.Billing.Application/Invoices/RegisterInvoiceHandler.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:naming-collaborators", "dotnet:domain-events"},
    ("src/Acme.Billing.Infrastructure/BillingDbContext.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "efcore:persistence"},
    ("src/Acme.Billing.Infrastructure/Migrations/20260101000000_Init.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "efcore:persistence"},
    ("src/Acme.Billing.Api/Invoices/InvoiceMappers.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:mapping"},
    ("src/Acme.Billing.Application/Invoices/RegisterInvoiceValidator.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:validation"},
    ("src/Acme.Billing.Infrastructure/Seeding/InvoiceSeeder.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:seeding"},
    ("proto/authz/v1/authz.proto", ""): {"dotnet:proto"},
    ("api/src/Acme.Authz.Domain/Events/OrderCancelledDomainEvent.cs", "public sealed record OrderCancelledDomainEvent(Guid OrderId) : IDomainEvent;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-events"},
    ("src/Acme.Billing.Application/Events/OrderCancelledDomainEventHandler.cs", "internal sealed class OrderCancelledDomainEventHandler : IPreCommitDomainEventHandler<OrderCancelledDomainEvent>"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:domain-events", "dotnet:naming-collaborators"},
    ("src/Acme.Billing.Infrastructure/Messaging/OrderCancelledEventPublisher.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:domain-events", "dotnet:naming-collaborators", "dotnet:messaging"},
    ("src/Acme.Billing.Infrastructure/Messaging/OrderCancelledEventConsumer.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:domain-events", "dotnet:naming-collaborators"},
    ("src/Acme.Billing.Infrastructure/Messaging/OrderEventsProcessor.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:messaging"},
    ("src/Acme.Billing.Application/Orders/OrderService.cs", "private readonly IIntegrationEventPublisher integrationEventPublisher;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:messaging"},
    ("src/Acme.Billing.Application/Orders/OrderPlacedReaction.cs", "internal sealed class OrderPlacedReaction : IIntegrationEventHandler<OrderPlacedEvent>"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:domain-events"},
    ("src/Acme.Billing.Domain/Invoice.cs", "    /// <summary>The issued invoice.</summary>"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:comments"},
    ("src/Acme.Billing.Infrastructure/Startup/ModuleRegistration.cs", "services.AddScoped<IOrderRepository, OrderRepository>();"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:dependency-injection"},
    ("src/Acme.Billing.Application/Pricing/DiscountResolver.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:naming-collaborators"},
    ("src/Acme.Billing.Domain/Order.cs", "public sealed class Order : IAggregateRoot"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-ddd"},
    ("src/Acme.Billing.Domain/Money.cs", "public readonly record struct Money(decimal Amount);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-values"},
    ("src/Acme.Billing.Domain/Sku.cs", "public static bool TryParse(string? text, [MaybeNullWhen(false)] out Sku sku)"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-values"},
    ("src/Acme.Billing.Domain/Invoices/InvoiceEntity.cs", "public sealed class InvoiceEntity : BaseEntity<Guid>"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-ddd"},
    ("src/Acme.Billing.Application/Orders/OrderLookup.cs", "var error = await lookup.FindAsync(id).MapError(OrderErrors.From);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:errors-carriers"},
    ("src/Acme.Billing.Infrastructure/Configurations/InvoiceConfiguration.cs", "builder.HasQueryFilter(invoice => !invoice.IsDeleted);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules"},
    ("src/Acme.Billing.Application/Orders/OrderService.cs", "public async Task<Result<Order, PlaceOrderError>> PlaceAsync()"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:errors", "dotnet:errors-carriers"},
    ("src/Acme.Billing.Application/Orders/PlaceOrderError.cs", "public partial record PlaceOrderError : IError"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:errors", "dotnet:errors-results"},
    ("src/Acme.Billing.Web/Orders/OrdersController.cs", "return result.ToOkOrProblem();"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:http-api", "dotnet:errors-terminals"},
    ("src/Acme.Billing.Infrastructure/Fulfilment/FulfilmentRegistration.cs", "services.AddKeyedScoped<IFulfilmentStep, CourierStep>(FulfilmentMode.Courier);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:keyed-strategies"},
    ("src/Acme.Billing.Infrastructure/Fulfilment/FulfilmentRegistration.Unions.cs", "    .Case<IFulfilToAddress>(arm => arm.Use<CourierFulfil>(FulfilmentMode.Courier))"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:keyed-unions"},
    ("src/Acme.Billing.Web/Program.cs", "builder.Services.AddGrpcClient<Orders.OrdersClient>();"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:dependency-injection", "dotnet:microservice-boundaries"},
    ("src/Acme.Billing.Infrastructure/Configurations/OrderConfiguration.cs", "builder.HasQueryFilter(order => order.TenantId == tenantContext.TenantId);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "efcore:multitenancy"},
    ("Directory.Packages.props", '<PackageVersion Include="Meziantou.Analyzer" Version="3.0.299" />'): {"dotnet:build", "dotnet:libraries", "dotnet:structure", "dotnet:libraries-selected"},
    (".scaffold.json", '{"options": {"architecture": "single-service"}}'): {"dotnet:structure-single-service"},
    ("src/Acme.Billing.Web/Acme.Billing.Web.csproj", '<Project Sdk="Microsoft.NET.Sdk.Web"></Project>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure"},
    ("Acme.Billing.slnx", '<Solution>\n  <Project Path="src/Acme.Billing.Application/Acme.Billing.Application.csproj" />\n</Solution>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure", "dotnet:structure-single-service"},
    ("Acme.Shop.slnx", '<Solution>\n  <Project Path="Billing/Modules/Invoices/Acme.Shop.Billing.Invoices.Application/Acme.Shop.Billing.Invoices.Application.csproj" />\n</Solution>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure"},
    ("Acme.Platform.slnx", '<Solution>\n  <Project Path="src/Acme.Ledger.Application/Acme.Ledger.Application.csproj" />\n  <Project Path="src/Acme.Audit.Application/Acme.Audit.Application.csproj" />\n</Solution>'): {"dotnet:build", "dotnet:libraries", "dotnet:structure"},
    ("src/Acme.Billing.Domain/Orders/Order.cs", "public sealed class Order(Guid id) : Entity<Guid>(id)"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:domain-design", "dotnet:domain-ddd"},
    ("src/Acme.Billing.Application/Payments/PaymentSession.cs", "public static bool TryCreate(\n    string reference,\n    out PaymentSession session)"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:domain-values"},
    ("src/Acme.Billing.Infrastructure/Data/TenantFilters.cs", "builder.HasQueryFilter(Key, entity =>\n    entity.TenantId == context.TenantId);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "efcore:multitenancy"},
    ("src/Acme.Billing.Infrastructure/Repositories/ScopedRepository.cs", "internal interface IScopedRepository<TEntity> where TEntity : class, IEntity<Guid>;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:repositories"},
    ("src/Acme.Billing.Application/Fulfilment/IFulfilmentUnionFactory.cs", "internal interface IFulfilmentUnionFactory;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:naming-collaborators", "dotnet:keyed-unions"},
    ("src/Acme.Billing.Infrastructure/Specifications/OrdersByStatusSpecification.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:naming-collaborators", "efcore:specification"},
    ("src/Acme.Billing.Infrastructure/Queries/OrderQueryBuilder.cs", ""): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:naming-collaborators", "efcore:query-building"},
    ("src/Acme.Billing.Infrastructure/Interceptors/DispatchInterceptor.cs", "internal sealed class DispatchInterceptor : SaveChangesInterceptor;"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "efcore:persistence", "efcore:event-dispatch"},
    ("src/Acme.Billing.Infrastructure/Repositories/EfInvoiceRepository.cs", "return await query.ToListAsync(ct);"): {"dotnet:style", "dotnet:naming", "dotnet:fields", "dotnet:structure-modules", "dotnet:repositories", "efcore:persistence"},
    ("plans/skill-routes/PLAN.md", ""): {"engineering:plans"},
    ("reviews/Feature-SkillRoutes/REVIEW.md", ""): {"engineering:review-lifecycle"},
    ("AGENTS.md", ""): {"engineering:docs"},
    ("db/migrations/0001_init.sql", ""): set(),
    ("model/authorization-model.fga", ""): set(),
    (".github/workflows/ci.yml", ""): set(),
}


class RouteDerivationTests(unittest.TestCase):
    def test_carved_tree_resolves_expected_skills(self) -> None:
        for (path, content), expected in CARVED_TREE.items():
            with self.subTest(path=path):
                self.assertEqual(expected, generator.skills_for("efcore-service", path, content))

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
        routes = generator.routes("efcore-service")["routes"]
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
                matched = generator.skills_for("efcore-service", path, content)
                self.assertLessEqual({"dotnet:style", "dotnet:naming", "dotnet:fields"}, matched)

    def test_rows_port_between_monorepo_and_carved_layouts(self) -> None:
        for (path, content), expected in CARVED_TREE.items():
            if not path.startswith("api/"):
                continue
            with self.subTest(path=path):
                self.assertEqual(expected, generator.skills_for("efcore-service", path[len("api/"):], content))

    def test_no_row_is_dead_on_the_simulated_tree(self) -> None:
        for index, route in enumerate(generator.routes("efcore-service")["routes"]):
            needle = route.get("content_requires")
            fired = any(
                re.search(route["path"], path) and (not needle or re.search(needle, content))
                for (path, content) in CARVED_TREE
            )
            self.assertTrue(fired, f"route {index} ({route['path']}) matches nothing in the simulated tree")

    def test_every_contract_skill_has_an_evidence_row(self) -> None:
        routed = {
            identifier
            for route in generator.routes("efcore-service")["routes"]
            for identifier in route["skills"]
            if identifier.startswith(("dotnet:", "efcore:"))
        }
        contracts = {
            f"{plugin}:" + re.search(r"^name: (.+)$", path.read_text(encoding="utf-8"), re.M).group(1)
            for plugin in ("dotnet", "efcore")
            for path in (ROOT / f".agents/{plugin}/contract").rglob("SKILL.md")
        } - {"dotnet:explanation"}
        self.assertTrue(contracts)
        self.assertEqual(set(), contracts - routed)

    def test_generic_dotnet_routes_do_not_require_efcore(self) -> None:
        declaration = generator.routes("dotnet-service")
        self.assertNotIn("efcore", declaration["layers"])
        self.assertTrue(all(not skill.startswith("efcore:") for row in declaration["routes"] for skill in row["skills"]))
        for path, content in CARVED_TREE:
            with self.subTest(path=path):
                expected = {skill for skill in generator.skills_for("efcore-service", path, content) if not skill.startswith("efcore:")}
                self.assertEqual(expected, generator.skills_for("dotnet-service", path, content))

    def test_route_path_strings_are_pairwise_distinct(self) -> None:
        paths = [route["path"] for route in generator.routes("efcore-service")["routes"]]
        self.assertEqual(len(paths), len(set(paths)), "skill_router keys seen-state on the path string")

    def test_routed_skills_resolve_and_stay_inside_the_layers(self) -> None:
        declaration = generator.routes("efcore-service")
        root = core_root()
        for route in declaration["routes"]:
            for identifier in route["skills"]:
                package, capability = identifier.split(":")
                self.assertIn(package, declaration["layers"])
                if package in ("dotnet", "efcore"):
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
            written = self.run_generator("--kind", "efcore-service", "--into", str(root))
            self.assertEqual(0, written.returncode, written.stdout + written.stderr)
            table = json.loads((root / ".agents/skill-routes.json").read_text(encoding="utf-8"))
            self.assertEqual(generator.routes("efcore-service"), table)
            current = self.run_generator("--kind", "efcore-service", "--into", str(root), "--check")
            self.assertEqual(0, current.returncode, current.stdout + current.stderr)
            (root / ".agents/skill-routes.json").write_text("{}", encoding="utf-8")
            stale = self.run_generator("--kind", "efcore-service", "--into", str(root), "--check")
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

    def test_shipped_tier_declarations_carry_current_routes(self) -> None:
        current = self.run_generator("--emit-tiers", str(ROOT), "--check")
        self.assertEqual(0, current.returncode, current.stdout + current.stderr)

    def test_tier_routes_gate_every_csharp_file_with_only_their_own_skills(self) -> None:
        dotnet = generator.tier_routes("dotnet")
        efcore = generator.tier_routes("efcore")
        self.assertTrue(all(skill.startswith("dotnet:") for row in dotnet for skill in row["skills"]))
        self.assertTrue(all(skill.startswith("efcore:") for row in efcore for skill in row["skills"]))
        floor = {skill for row in dotnet if re.search(row["path"], "src/Acme.Outbox/OutboxRelay.cs")
                 and not row.get("content_requires") for skill in row["skills"]}
        self.assertEqual({"dotnet:style", "dotnet:naming", "dotnet:fields"}, floor)

    def test_emit_tiers_rewrites_a_stale_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".agents/tiers").mkdir(parents=True)
            for tier in ("dotnet", "efcore"):
                source = json.loads((ROOT / f".agents/tiers/{tier}.json").read_text(encoding="utf-8"))
                source.pop("routes")
                (root / f".agents/tiers/{tier}.json").write_text(json.dumps(source), encoding="utf-8")
            stale = self.run_generator("--emit-tiers", str(root), "--check")
            self.assertEqual(1, stale.returncode)
            written = self.run_generator("--emit-tiers", str(root))
            self.assertEqual(0, written.returncode, written.stdout + written.stderr)
            tier = json.loads((root / ".agents/tiers/dotnet.json").read_text(encoding="utf-8"))
            self.assertEqual(generator.tier_routes("dotnet"), tier["routes"])
            self.assertEqual("tj-agents/dotnet", tier["owner_repository"][0])

    def test_emit_registry_cannot_be_combined_with_kind(self) -> None:
        result = self.run_generator("--emit-registry", "routes", "--kind", "efcore-service", "--into", ".")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot be combined", result.stderr)

    def test_kind_requires_into(self) -> None:
        result = self.run_generator("--kind", "efcore-service")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--kind and --into are required", result.stderr)

    def test_unknown_kind_is_rejected(self) -> None:
        result = self.run_generator("--kind", "react-app", "--into", ".")
        self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
