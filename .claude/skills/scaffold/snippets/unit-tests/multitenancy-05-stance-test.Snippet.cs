namespace SnippetFixtures.Multitenancy05;

using Microsoft.EntityFrameworkCore;
using Xunit;

#pragma warning disable MA0004

internal static class Example
{
    private static readonly Type[] TenantFilteredTypes = [];

    public static async Task Run(ReadDbContext readContext, TenantScopedDbContext tenantContext)
    {
// snippet:begin
Assert.IsAssignableFrom<IReadDbContext>(readContext);
Assert.False(typeof(IDbContext).IsAssignableFrom(readContext.GetType()));
Assert.Equal(QueryTrackingBehavior.NoTracking, readContext.ChangeTracker.QueryTrackingBehavior);
await Assert.ThrowsAsync<InvalidOperationException>(() => readContext.SaveChangesAsync());
Assert.All(TenantFilteredTypes, type =>
    Assert.Empty(readContext.Model.FindEntityType(type)!.GetDeclaredQueryFilters()));
Assert.All(TenantFilteredTypes, type =>
    Assert.NotEmpty(tenantContext.Model.FindEntityType(type)!.GetDeclaredQueryFilters()));
// snippet:end

    }
}

#pragma warning restore MA0004
