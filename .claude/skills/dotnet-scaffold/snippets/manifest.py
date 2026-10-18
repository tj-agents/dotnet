from __future__ import annotations

from typing import Optional, TypedDict


class Snippet(TypedDict):
    id: str
    owner: str
    skill: str
    block: int
    project: str
    namespace: str
    header: str
    footer: str
    skip: Optional[str]


def entry(
    id: str, skill: str, block: int, project: str, namespace: str,
    header: str = "", footer: str = "", skip: Optional[str] = None, owner: str = "dotnet",
) -> Snippet:
    return {
        "id": id, "owner": owner, "skill": skill, "block": block, "project": project,
        "namespace": namespace, "header": header, "footer": footer, "skip": skip,
    }


SNIPPETS: list[Snippet] = [
    entry("fields-01-private-fields", "fields/SKILL.md", 1, "infrastructure", "SnippetFixtures.Fields01",
          header="internal sealed class OrderDbContext;\n\n#pragma warning disable CS0169, CS8618\n\ninternal sealed class OrderService\n{\n",
          footer="\n}\n\n#pragma warning restore CS0169, CS8618\n"),
    entry("fields-02-no-shadow", "fields/SKILL.md", 2, "infrastructure", "SnippetFixtures.Fields02",
          header=(
              "internal sealed class StockCatalog;\n"
              "internal sealed class Inventory(StockCatalog catalog)\n{\n"
              "    private readonly StockCatalog catalog = catalog;\n}\n\n"
              "internal sealed class InventoryTests\n{\n"
          ),
          footer="\n}\n"),
    entry("style-01-null-check", "style/SKILL.md", 1, "infrastructure", "SnippetFixtures.Style01",
          skip="three independent inline examples (CORRECT, CORRECT, WRONG) each assuming their own scope for a `tenantId` identifier — the second introduces a fresh pattern-bound `tenantId` and the third reuses the first's, so flattened into one method body the declarations collide (CS0136/CS0841); splitting them would require inserting braces inside the verbatim region."),
    entry("style-02-null-bang", "style/SKILL.md", 2, "infrastructure", "SnippetFixtures.Style02",
          skip="two side-by-side fragments at different syntactic levels (a class member default and a local variable statement) that cannot share one compilable unit without altering the verbatim text, plus a duplicate `DisplayName` member (CS0102) between the correct and wrong halves."),
    entry("style-03-braces", "style/SKILL.md", 3, "infrastructure", "SnippetFixtures.Style03",
          skip="a bare `catch` clause with no preceding `try` is a hard syntax error (not a warning), so it cannot share a compilable method body with the preceding guard-clause example without altering the verbatim text."),
    entry("style-04-optional-param", "style/SKILL.md", 4, "infrastructure", "SnippetFixtures.Style04",
          skip="`private Task<int> PlaceAsync(...);` is a body-less signature (illustrating a name only), which is not a legal member on a concrete class; it is pseudocode, not compilable C#."),
    entry("fields-03-base-call", "fields/SKILL.md", 3, "infrastructure", "SnippetFixtures.Fields03",
          header=(
              "using Microsoft.EntityFrameworkCore;\n\n"
              "#pragma warning disable CS0162\n\n"
              "internal class Entity\n{\n    public bool IsActive { get; set; }\n}\n\n"
              "internal class RepositoryBase\n{\n"
              "    protected IQueryable<Entity> CurrentScope { get; } = new List<Entity>().AsQueryable();\n}\n\n"
              "internal sealed class Repository : RepositoryBase\n{\n"
              "    public async Task<List<Entity>> GetActiveAsync(CancellationToken ct)\n    {\n"
          ),
          footer="\n    }\n}\n\n#pragma warning restore CS0162\n"),
    entry("comments-01", "comments/SKILL.md", 1, "infrastructure", "SnippetFixtures.Comments01",
          skip="the CORRECT and WRONG halves declare the same `TenantId` member twice (CS0102), so they cannot share one compilable unit without altering the verbatim text."),

    entry("di-01-dependency-holder", "dependency-injection/SKILL.md", 1, "infrastructure", "SnippetFixtures.DependencyInjection01",
          header=(
              "internal sealed class ReserveStockStep : IReserveStep;\n"
              "internal sealed class ChargeCardStep : IChargeStep;\n"
              "internal sealed class DispatchStep : IDispatchStep;\n"
              "internal interface IReserveStep;\n"
              "internal interface IChargeStep;\n"
              "internal interface IDispatchStep;\n"
              "internal interface IFulfilmentFlow;\n\n"
          )),

    entry("logging-01-logger-message", "logging/SKILL.md", 1, "infrastructure", "SnippetFixtures.Logging01",
          header="using Microsoft.Extensions.Logging;\n\ninternal static partial class Log01\n{\n",
          footer="\n}\n"),

    entry("mapping-01-xmappers", "mapping/SKILL.md", 1, "infrastructure", "SnippetFixtures.Mapping01",
          header=(
              "internal sealed class ShipmentEntity\n{\n"
              "    public Guid Id { get; init; }\n    public string TrackingReference { get; init; } = null!;\n}\n\n"
              "internal sealed record Shipment(Guid Id, string TrackingReference);\n\n"
          )),

    entry("messaging-01-publisher", "messaging/SKILL.md", 1, "infrastructure", "SnippetFixtures.Messaging01",
          header=""),

    entry("domain-events-01-raiser", "domain/events/SKILL.md", 1, "infrastructure", "SnippetFixtures.DomainEvents01",
          header=""
                 "internal sealed record OrderCancelledDomainEvent(object Order) : IDomainEvent;\n\n"
                 "public enum OrderStatus { Cancelled }\n\n"),
    entry("domain-events-02-handler", "domain/events/SKILL.md", 2, "infrastructure", "SnippetFixtures.DomainEvents02",
          header=(
              ""
              "public sealed class OrderEntity\n{\n"
              "    public Guid Id { get; init; }\n    public Guid CustomerId { get; init; }\n    public DateTimeOffset CancelledAt { get; init; }\n}\n"
              "\n"
          )),
    entry("domain-events-03-registration", "domain/events/SKILL.md", 3, "infrastructure", "SnippetFixtures.DomainEvents03",
          header=(
              "using Microsoft.Extensions.DependencyInjection;\n\n"
              "internal sealed record OrderCancelledDomainEvent(object Order) : IDomainEvent;\n"
              "internal sealed class OrderCancelledDomainEventHandler : IDomainEventHandler<OrderCancelledDomainEvent>\n{\n"
              "    public Task HandleAsync(OrderCancelledDomainEvent domainEvent, CancellationToken ct = default) => Task.CompletedTask;\n}\n\n"
              "internal static class Registration\n{\n    public static void Register(IServiceCollection services)\n    {\n"
          ),
          footer="\n    }\n}\n"),

    entry("messaging-02-processor", "messaging/SKILL.md", 2, "infrastructure", "SnippetFixtures.Messaging02",
          header=(
              "using Azure.Messaging.ServiceBus;\n"
              "using Microsoft.Extensions.DependencyInjection;\n"
              "using Microsoft.Extensions.Hosting;\n"
              "using Microsoft.Extensions.Logging;\n\n"
              "internal sealed record OrderPlacedEvent : IIntegrationEvent;\n\n"
              "internal static partial class Log02\n{\n"
              "    [LoggerMessage(Level = LogLevel.Error, Message = \"Subscription {EntityPath} processing failed\")]\n"
              "    internal static partial void SubscriptionProcessingFailed(this ILogger logger, string entityPath, Exception exception);\n}\n\n"
          )),

    entry("keyed-strategies-01-factory", "keyed/strategies/SKILL.md", 1, "infrastructure", "SnippetFixtures.KeyedStrategies01",
          header="using Microsoft.Extensions.DependencyInjection;\n\ninternal enum FulfilmentMode { Digital, Collection, Courier, Freight }\n\n"),
    entry("keyed-strategies-02-builder", "keyed/strategies/SKILL.md", 2, "infrastructure", "SnippetFixtures.KeyedStrategies02",
          skip="the registration calls depend on the undeclared AddFulfilmentStrategies/For/AddSingleton/RequireAll builder API and leaf contracts; compiling this standalone would require inventing the missing registration-builder implementation and contract declarations."),
    entry("keyed-strategies-03-registration", "keyed/strategies/SKILL.md", 3, "infrastructure", "SnippetFixtures.KeyedStrategies03",
          skip="prose-adjacent fragment with no named types shown; nothing concrete to stub without inventing content the doc doesn't specify."),
    entry("keyed-strategies-04-call-site", "keyed/strategies/SKILL.md", 4, "infrastructure", "SnippetFixtures.KeyedStrategies04"),

    entry("keyed-unions-01-match", "keyed/unions/SKILL.md", 1, "infrastructure", "SnippetFixtures.KeyedUnions01",
          header=(
              "using Dunet;\n\n"
              "public enum FulfilmentMode { Digital, Collection, Courier, Freight }\n"
              "public sealed record Parcel;\n"
              "public sealed record Order(Guid Id)\n{\n    public FulfilmentMode Mode { get; init; }\n}\n"
              "public sealed record Address;\n"
              "internal sealed record FulfilmentRequest(Address Address);\n"
              "public interface IFulfil { object Fulfil(Parcel parcel, Order order); }\n"
              "public interface IFulfilToAddress { object Fulfil(Parcel parcel, Order order, Address address); }\n\n"
              "[Union]\n"
              "public abstract partial record Fulfilment\n{\n"
              "    public partial record Fulfil(IFulfil Value);\n"
              "    public partial record FulfilToAddress(IFulfilToAddress Value);\n}\n\n"
              "internal interface IFulfilmentFactory { Fulfilment Create(FulfilmentMode mode); }\n\n"
              "internal static class Example\n{\n"
              "    public static object Handle(IFulfilmentFactory fulfilmentFactory, Parcel parcel, Order order, FulfilmentRequest request)\n    {\n"
          ),
          footer="\n        return result;\n    }\n}\n"),
    entry("keyed-unions-02-registration", "keyed/unions/SKILL.md", 2, "infrastructure", "SnippetFixtures.KeyedUnions02",
          header=(
              "internal enum FulfilmentMode { Digital, Collection, Courier, Freight }\n"
              "internal sealed record Parcel;\n"
              "internal sealed record Order(Guid Id);\n"
              "internal sealed record Address;\n"
              "internal interface IFulfil;\n"
              "internal interface IFulfilToAddress;\n"
              "internal sealed class DigitalFulfil : IFulfil;\n"
              "internal sealed class CollectionFulfil : IFulfil;\n"
              "internal sealed class CourierFulfil : IFulfilToAddress;\n"
              "internal abstract record Fulfilment\n{\n"
              "    public sealed record Fulfil(IFulfil Value) : Fulfilment;\n"
              "    public sealed record FulfilToAddress(IFulfilToAddress Value) : Fulfilment;\n}\n\n"
              "internal sealed class UnionCaseBuilder<TUnion>\n{\n"
              "    public UnionCaseBuilder<TUnion> Case<TInterface>(Func<TInterface, TUnion> wrap) => this;\n"
              "    public UnionCaseBuilder<TUnion> Use<TImplementation>(params FulfilmentMode[] modes) => this;\n}\n\n"
              "internal static class Example\n{\n"
              "    public static void Register(UnionCaseBuilder<Fulfilment> union)\n    {\n"
          ),
          footer="\n    }\n}\n"),

    entry("errors-carriers-01-nullable-option", "errors/carriers/SKILL.md", 1, "infrastructure", "SnippetFixtures.ErrorsCarriers01",
          skip="mixes two top-level interface declarations with a class-member method fragment (referencing an instance `repository` field not shown in the block) at different syntactic levels; not one compilable unit without altering the verbatim text."),
    entry("errors-carriers-02-resolver", "errors/carriers/SKILL.md", 2, "infrastructure", "SnippetFixtures.ErrorsCarriers02",
          header="public sealed record OrderSnapshot;\n\n"),
    entry("errors-carriers-03-target-typed", "errors/carriers/SKILL.md", 3, "infrastructure", "SnippetFixtures.ErrorsCarriers03",
          header=(
              ""
              "internal sealed record User;\n"
              "internal abstract record LookupUserError\n{\n    public sealed record NotFound : LookupUserError;\n}\n"
              "internal abstract record CreateUserError\n{\n    public sealed record EmailInUse : CreateUserError;\n}\n"
              "internal abstract record ChangePasswordError\n{\n    public sealed record InvalidPassword : ChangePasswordError;\n}\n\n"
              "internal static class Example\n{\n"
              "    public static void Run(User user)\n    {\n"
          ),
          footer="\n    }\n}\n"),
    entry("errors-carriers-04-method-form", "errors/carriers/SKILL.md", 4, "infrastructure", "SnippetFixtures.ErrorsCarriers04",
          header=(
              ""
              "internal abstract record ChangePasswordError\n{\n    public sealed record InvalidPassword : ChangePasswordError;\n}\n\n"
              "internal sealed class User\n{\n    public Guid Id { get; init; }\n}\n\n"
              "internal sealed class UserStore\n{\n"
              "    private readonly List<User> users = [];\n\n"
              "    private static bool IsAllowed(string password) => true;\n"
              "    private void SetPassword(string password) { }\n\n"
          ),
          footer="\n}\n"),
    entry("errors-carriers-05-named-cases", "errors/carriers/SKILL.md", 5, "infrastructure", "SnippetFixtures.ErrorsCarriers05",
          header="internal static class Example\n{\n    public static void Run(string value, string error)\n    {\n",
          footer="\n    }\n}\n"),
    entry("errors-carriers-06-orfailure", "errors/carriers/SKILL.md", 6, "infrastructure", "SnippetFixtures.ErrorsCarriers06",
          header=(
              ""
              "internal sealed record WarehouseDetails;\n"
              "internal abstract record GetWarehouseError\n{\n    public sealed record WarehouseNotFound : GetWarehouseError;\n}\n\n"
              "internal interface IWarehouseService2 { Task<Option<WarehouseDetails>> GetDetailsByIdAsync(int id); }\n\n"
              "#pragma warning disable CS8321\n\n"
              "internal static class Example\n{\n"
              "    public static async Task<Result<WarehouseDetails, GetWarehouseError>> GetAsync(IWarehouseService2 warehouseService, int id)\n    {\n"
              "        "
          ),
          footer="\n        return warehouse;\n    }\n}\n\n#pragma warning restore CS8321\n"),
    entry("errors-carriers-07-checkout", "errors/carriers/SKILL.md", 7, "infrastructure", "SnippetFixtures.ErrorsCarriers07",
          header=(
              ""
              "internal sealed record Order;\n"
              "internal sealed record Checkout;\n"
              "internal abstract record CheckoutError\n{\n"
              "    public sealed record OrderNotFound(int OrderId) : CheckoutError;\n"
              "    public sealed record Invalid(ValidationErrors Errors) : CheckoutError;\n}\n\n"
              "internal interface IOrderModule { Task<Option<Order>> GetByIdAsync(int orderId); }\n"
              "internal interface IOrderValidator { ValidationResult ValidateCheckout(Order order, int quantity); }\n\n"
              "internal sealed class Example\n{\n"
              "    private readonly IOrderModule orderModule;\n"
              "    private readonly IOrderValidator orderValidator;\n\n"
              "    public Example(IOrderModule orderModule, IOrderValidator orderValidator)\n    {\n"
              "        this.orderModule = orderModule;\n"
              "        this.orderValidator = orderValidator;\n    }\n\n"
              "    private static Task<Checkout> CreateCheckoutAsync(Order order, int quantity) => Task.FromResult(new Checkout());\n\n"
              "    "
          ),
          footer="\n}\n"),
    entry("errors-carriers-08-nullcoalesce", "errors/carriers/SKILL.md", 8, "infrastructure", "SnippetFixtures.ErrorsCarriers08",
          header="internal static class Example\n{\n    public static void Run(Option<string> option)\n    {\n",
          footer="\n    }\n}\n"),
    entry("errors-carriers-09-native-union", "errors/carriers/SKILL.md", 9, "infrastructure", "SnippetFixtures.ErrorsCarriers09",
          skip="documents a net11.0-only Reunion feature (compiler-recognized native unions); the scaffold targets net10.0 exclusively, so this cannot compile under it."),

    entry("errors-results-01-payment-union", "errors/results/SKILL.md", 1, "infrastructure", "SnippetFixtures.ErrorsResults01",
          header="using Dunet;\n\n"),
    entry("errors-results-02-refund-union", "errors/results/SKILL.md", 2, "infrastructure", "SnippetFixtures.ErrorsResults02",
          header=(
              "using Dunet;\n\n"
              "[Union(EnableImplicitConversions = false)]\n"
              "public abstract partial record PaymentError : IError\n{\n"
              "    public ErrorDefinition Definition => this switch\n    {\n"
              "        PayerNotFound => ErrorDefinition.NotFound<PayerNotFound>(),\n"
              "        Declined => ErrorDefinition.PaymentRequired<Declined>(\"The payment was declined.\"),\n"
              "        ProviderFailure => ErrorDefinition.Invalid<ProviderFailure>(\"The payment provider rejected the request.\")\n    };\n\n"
              "    public partial record PayerNotFound;\n"
              "    public partial record Declined;\n"
              "    public partial record ProviderFailure(string ProviderCode);\n}\n\n"
          )),

    entry("errors-terminals-01-ok-or", "errors/terminals/SKILL.md", 1, "web", "SnippetFixtures.ErrorsTerminals01",
          header=(
              "using Microsoft.AspNetCore.Mvc;\n\n"
              "internal sealed record ArtistDetails\n{\n    public object ToDetailsResponse() => this;\n}\n\n"
              "internal abstract record GetArtistError : IError\n{\n"
              "    public sealed record ArtistNotFound : GetArtistError;\n"
              "    public ErrorDefinition Definition => ErrorDefinition.NotFound<GetArtistError>();\n}\n\n"
              "internal static class ResultWebExtensions\n{\n"
              "    public static IActionResult ToOkOr<T>(this Option<T> option, Func<IActionResult> onNone) =>\n"
              "        option.Match(value => new OkObjectResult(value), onNone);\n\n"
              "    public static IActionResult ToOkOr<T, TMapped>(this Option<T> option, Func<T, TMapped> map, Func<IActionResult> onNone) =>\n"
              "        option.Match(value => (IActionResult)new OkObjectResult(map(value)), onNone);\n\n"
              "    public static IActionResult ToOkOrProblem<T, TMapped, TError>(this Result<T, TError> result, Func<T, TMapped> map)\n        where TError : IError =>\n"
              "        result.Match(\n"
              "            value => (IActionResult)new OkObjectResult(map(value)),\n"
              "            error => new ObjectResult(error.Definition.Message) { StatusCode = 400 });\n}\n\n"
              "internal sealed class ArtistController : ControllerBase\n{\n"
              "    private static IActionResult Unauthorized2() => new UnauthorizedResult();\n"
              "    private static IActionResult NotFound2() => new NotFoundResult();\n\n"
              "    public IActionResult Get(Option<string> user, Option<ArtistDetails> artist, Result<ArtistDetails, GetArtistError> artistResult)\n    {\n"
              "#pragma warning disable CS0162\n"
          ),
          footer="\n        return Unauthorized2();\n#pragma warning restore CS0162\n    }\n}\n"),

    entry("validation-01-combine", "validation/SKILL.md", 1, "infrastructure", "SnippetFixtures.Validation01",
          header=(
              ""
              "internal sealed record NameRequest(string Name, string Email);\n\n"
              "internal static class Example\n{\n"
              "    private static ValidationResult ValidateName(string name) => ValidationResult.Valid;\n"
              "    private static ValidationResult ValidateEmail(string email) => ValidationResult.Valid;\n\n"
              "    public static void Run(NameRequest request)\n    {\n"
          ),
          footer="\n    }\n}\n"),
    entry("validation-02-ensure", "validation/SKILL.md", 2, "infrastructure", "SnippetFixtures.Validation02",
          header=(
              ""
              "internal sealed record Order;\n"
              "internal abstract record CheckoutError\n{\n"
              "    public sealed record OrderNotFound(int OrderId) : CheckoutError;\n"
              "    public sealed record Invalid(ValidationErrors Errors) : CheckoutError;\n}\n\n"
              "internal interface IOrderModule { Task<Option<Order>> GetByIdAsync(int orderId); }\n"
              "internal interface IOrderValidator { ValidationResult ValidateCheckout(Order order, int quantity); }\n\n"
              "internal static class Example\n{\n"
              "    public static Task<Result<Order, CheckoutError>> Run(IOrderModule orderModule, IOrderValidator orderValidator, int orderId, int quantity)\n    {\n        "
          ),
          footer="\n    }\n}\n"),
    entry("validation-03-place-order-union", "validation/SKILL.md", 3, "infrastructure", "SnippetFixtures.Validation03",
          header="using Dunet;\n\n"),

    entry("testing-hub-01-naming", "testing/SKILL.md", 1, "unit-tests", "SnippetFixtures.TestingHub01",
          header="using Xunit;\n\ninternal sealed class Calculator\n{\n    public int Add(int left, int right) => left + right;\n}\n\npublic sealed class CalculatorNamingExample\n{\n    private readonly Calculator calculator = new();\n\n    [Theory]\n    [InlineData(2, 3, 5)]\n    ",
          footer="\n    {\n        var result = calculator.Add(left, right);\n\n        Assert.Equal(expected, result);\n    }\n}\n"),
    entry("testing-unit-01-inventory", "testing/unit/SKILL.md", 1, "unit-tests", "SnippetFixtures.TestingUnit01",
          header="using Xunit;\n\ninternal sealed class StockCatalog;\n\ninternal sealed class Inventory(StockCatalog catalog)\n{\n"
                "    private readonly StockCatalog catalog = catalog;\n"
                "    private readonly Dictionary<string, int> stock = [];\n\n"
                "    public void Receive(string sku, int quantity) => stock[sku] = stock.GetValueOrDefault(sku) + quantity;\n\n"
                "    public int StockOf(string sku) => stock.GetValueOrDefault(sku);\n}\n\n"),
    entry("testing-integration-01-calculator", "testing/integration/SKILL.md", 1, "integration-tests", "SnippetFixtures.TestingIntegration01",
          header=(
              "using System.Net;\nusing System.Net.Http.Json;\nusing Microsoft.EntityFrameworkCore;\nusing Shouldly;\nusing Xunit;\n\n"
              "public sealed class SeedUser { public Guid Id { get; init; } }\n"
              "public sealed class SeedState { public SeedUser StandardUser { get; } = new(); }\n"
              "internal sealed class RunningTotal { public Guid UserId { get; init; } public decimal Value { get; init; } }\n"
              "internal interface ICalculatorReadDbContext { DbSet<RunningTotal> RunningTotals { get; } }\n"
              "internal sealed class CalculationResult { public decimal Total { get; init; } }\n"
              "public sealed class Scoped<T>\n{\n"
              "    private readonly T value;\n\n"
              "    public Scoped(T value)\n    {\n        this.value = value;\n    }\n\n"
              "    public Task<TResult> RunAsync<TResult>(Func<T, Task<TResult>> work) => work(value);\n}\n"
              "[CollectionDefinition(IntegrationCollection.Name)]\npublic sealed class IntegrationCollection : ICollectionFixture<ApiFixture>\n{\n    public const string Name = \"Integration\";\n}\n"
              "public sealed class ApiFixture\n{\n"
              "    public SeedState SeedState { get; } = new();\n\n"
              "    public HttpClient CreateClient(SeedUser user) => new() { BaseAddress = new Uri(\"https://localhost\") };\n\n"
              "    public Scoped<T> Scoped<T>() where T : class => new(default!);\n}\n\n"
          )),

    entry("testing-e2e-01-clock", "testing/e2e/SKILL.md", 1, "e2e-tests", "SnippetFixtures.TestingE2E01",
          header=""),

    entry("repositories-01-contract", "repositories/SKILL.md", 1, "infrastructure", "SnippetFixtures.Repositories01",
          header="public sealed record Order(Guid Id);\n\n"),
    entry("naming-collaborators-01-query-builder", "naming/collaborators/SKILL.md", 1, "infrastructure", "SnippetFixtures.NamingCollaborators01",
          header="using SnippetFixtures.EfQueryPatterns;\n\n"),
    entry("seeding-02-event-path", "seeding/SKILL.md", 1, "infrastructure", "SnippetFixtures.Seeding02",
          header=(
              "public sealed record OrderCreatedEvent(Guid Id) : IIntegrationEvent;\n\n"
              "public sealed class OrderSeedState\n{\n"
              "    public OrderCreatedEvent OrderCreated { get; } = new(Guid.Parse(\"61a662e9-123e-4b0c-925d-af7c2bedad8c\"));\n"
              "}\n\n"
          )),
    entry("efcore-multitenancy-01-entity-filter", "multitenancy/SKILL.md", 1, "infrastructure", "SnippetFixtures.EfMultitenancy01",
          owner="efcore", header="using Microsoft.EntityFrameworkCore;\nusing Microsoft.EntityFrameworkCore.Metadata.Builders;\n\n"),
    entry("efcore-event-dispatch-01-transaction", "event-dispatch/SKILL.md", 1, "infrastructure", "SnippetFixtures.EfEventDispatch01",
          owner="efcore", header=(
              "using Microsoft.EntityFrameworkCore;\n\n"
              "internal static class Example\n{\n"
              "    public static async Task SaveAndCommitAsync(DbContext context, CancellationToken ct = default)\n    {\n"
          ), footer="\n    }\n}\n"),

    entry("efcore-specification-01-ready-orders", "specification/SKILL.md", 1, "infrastructure", "SnippetFixtures.EfQueryPatterns",
          owner="efcore", header="using System.Linq.Expressions;\n\n"),
    entry("efcore-query-building-01-builder", "query-building/SKILL.md", 1, "infrastructure", "SnippetFixtures.EfQueryPatterns",
          owner="efcore"),
    entry("efcore-query-building-02-repository", "query-building/SKILL.md", 2, "infrastructure", "SnippetFixtures.EfQueryPatterns",
          owner="efcore", header="using Microsoft.EntityFrameworkCore;\n\n"),
    entry("efcore-query-building-03-registration", "query-building/SKILL.md", 3, "infrastructure", "SnippetFixtures.EfQueryPatterns",
          owner="efcore", header="using Microsoft.EntityFrameworkCore;\nusing Microsoft.Extensions.DependencyInjection;\n\n"),

    entry("persistence-01-exclude-from-migrations", "persistence/SKILL.md", 1, "infrastructure", "SnippetFixtures.Persistence01", owner="efcore",
          header=(
              "using Microsoft.EntityFrameworkCore;\nusing Microsoft.EntityFrameworkCore.Metadata.Builders;\n\n"
              "internal sealed class SellerRatingProjection;\n\n"
              "internal sealed class SellerRatingProjectionConfiguration : IEntityTypeConfiguration<SellerRatingProjection>\n{\n"
              "    public void Configure(EntityTypeBuilder<SellerRatingProjection> builder)\n    {\n"
          ),
          footer="\n    }\n}\n"),

    entry("seeding-01-seed-async", "persistence/SKILL.md", 2, "infrastructure", "SnippetFixtures.Seeding01", owner="efcore",
          header=(
              "using Microsoft.EntityFrameworkCore;\n\n"
              "internal sealed class Warehouse;\n"
              "internal sealed class SeedData { public List<Warehouse> Warehouses { get; } = []; }\n"
              "internal sealed class SeedContext\n{\n"
              "    public DbSet<Warehouse> Warehouses { get; } = null!;\n\n"
              "    public Task<bool> AnyWarehousesAsync(CancellationToken ct) => Warehouses.AnyAsync(ct);\n\n"
              "    public Task SaveChangesAsync(CancellationToken ct) => Task.CompletedTask;\n}\n\n"
              "internal sealed class Seeder\n{\n"
              "    private readonly SeedContext context;\n"
              "    private readonly SeedData seedData;\n\n"
              "    public Seeder(SeedContext context, SeedData seedData)\n    {\n"
              "        this.context = context;\n"
              "        this.seedData = seedData;\n    }\n\n"
          ),
          footer="\n}\n"),

    entry("proto-01-naming", "proto/SKILL.md", 1, "infrastructure", "SnippetFixtures.Proto01",
          skip="`(...)` is a literal ellipsis standing in for an elided parameter list and body; it is not valid C# syntax, so the contrast (proto-named vs domain-named payload) is illustrative only."),
    entry("proto-02-mappers", "proto/SKILL.md", 2, "infrastructure", "SnippetFixtures.Proto02",
          skip="`=> ...;` is a literal ellipsis standing in for an elided method body; it is not valid C# syntax."),
    entry("proto-03-error-map", "proto/SKILL.md", 3, "infrastructure", "SnippetFixtures.Proto03",
          header=(
              "using System.Collections.Frozen;\n\n"
              "internal abstract record OrderError : IError\n{\n"
              "    public ErrorDefinition Definition => ErrorDefinition.NotFound<OrderError>();\n\n"
              "    public sealed record CustomerNotFound : OrderError;\n"
              "    public sealed record AddressRejected : OrderError;\n}\n\n"
              "internal static class Example\n{\n"
          ),
          footer="\n}\n"),
    entry("proto-04-call-credentials", "proto/SKILL.md", 4, "infrastructure", "SnippetFixtures.Proto04",
          header=(
              "using Grpc.Core;\nusing Grpc.Net.ClientFactory;\nusing Microsoft.Extensions.DependencyInjection;\n\n"
              "internal interface ITokenService { Task<string> GetTokenAsync(string scope); }\n\n"
              "internal static class Example\n{\n    public static void Register(IServiceCollection services, string address)\n    {\n"
          ),
          footer="\n    }\n}\n"),
]
