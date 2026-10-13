namespace SnippetFixtures.Multitenancy02;

using Microsoft.EntityFrameworkCore;

internal static class Schema { public const string Name = "orders"; }
internal sealed class OrderConfigurationProvider;
internal sealed class OrderEntity;

// snippet:begin
internal interface IOrderReadDbContext
{
    IQueryable<OrderEntity> Orders { get; }
}

internal sealed class OrderReadDbContext(
    DbContextOptions<OrderReadDbContext> options,
    OrderConfigurationProvider provider)
    : ReadDbContext(options, provider, Schema.Name), IOrderReadDbContext
{
    IQueryable<OrderEntity> IOrderReadDbContext.Orders => Query<OrderEntity>();
}
// snippet:end
