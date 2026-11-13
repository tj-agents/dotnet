namespace SnippetFixtures.Concurrency02;

using Microsoft.EntityFrameworkCore;

internal sealed class TenantEntity { public Guid Id { get; set; } }
internal sealed class TenantDbContext : DbContext { public DbSet<TenantEntity> Tenants => Set<TenantEntity>(); }

internal sealed class TenantRepository
{
    private readonly TenantDbContext context;

    public TenantRepository(TenantDbContext context) => this.context = context;

// snippet:begin
public Task<TenantEntity?> GetByIdWithKeyShareLockAsync(Guid tenantId, CancellationToken ct = default) =>
    context.Tenants
        .FromSql($"""SELECT * FROM tenant."Tenants" WHERE "Id" = {tenantId} FOR KEY SHARE""")
        .SingleOrDefaultAsync(ct);
// snippet:end

}
