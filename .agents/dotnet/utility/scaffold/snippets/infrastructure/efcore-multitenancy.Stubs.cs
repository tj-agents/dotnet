using Microsoft.EntityFrameworkCore;

namespace SnippetFixtures.EfMultitenancy01;

public sealed class PrivateOrder
{
    public Guid Id { get; init; }
    public Guid TenantId { get; init; }
}

public sealed class PrivateReadDbContext : DbContext
{
    private readonly Guid tenantId;

    public PrivateReadDbContext(DbContextOptions<PrivateReadDbContext> options, Guid tenantId) : base(options)
    {
        this.tenantId = tenantId;
    }

    public Guid TenantId => tenantId;
}
