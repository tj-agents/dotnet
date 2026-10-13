namespace SnippetFixtures.Multitenancy03;

using Microsoft.EntityFrameworkCore;

internal static class Schema { public const string Name = "orders"; }
internal sealed class OrderConfigurationProvider;
internal sealed class OrderEntity;

// snippet:begin
internal sealed class OrderModerationDbContext(
    DbContextOptions<OrderModerationDbContext> options,
    OrderConfigurationProvider provider)
    : PrivilegedDbContext(options, provider, Schema.Name)
{
    public DbSet<OrderEntity> Orders => Set<OrderEntity>();
}
// snippet:end
