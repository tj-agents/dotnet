namespace SnippetFixtures.Multitenancy01;

using Microsoft.EntityFrameworkCore;

internal static class Schema { public const string Name = "orders"; }
internal sealed class OrderConfigurationProvider;
internal sealed class OrderEntity;
internal sealed class OrderLineEntity;
internal static class TenantFilterExtensions
{
    public static void ApplySingleOwner<TEntity>(this ModelBuilder builder, object context) { }
}

// snippet:begin
internal sealed class OrderDbContext(
    DbContextOptions<OrderDbContext> options,
    OrderConfigurationProvider provider,
    ITenantContext tenantContext)
    : TenantScopedDbContext(options, provider, tenantContext, Schema.Name)
{
    public DbSet<OrderEntity> Orders => Set<OrderEntity>();
    public DbSet<OrderLineEntity> OrderLines => Set<OrderLineEntity>();

    protected override void ApplyTenantFilters(ModelBuilder modelBuilder) =>
        modelBuilder.ApplySingleOwner<OrderEntity>(this);
}
// snippet:end
