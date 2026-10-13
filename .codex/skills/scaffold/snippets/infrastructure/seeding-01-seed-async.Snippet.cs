namespace SnippetFixtures.Seeding01;

using Microsoft.EntityFrameworkCore;

internal sealed class Warehouse;
internal sealed class SeedData { public List<Warehouse> Warehouses { get; } = []; }
internal sealed class SeedContext
{
    public DbSet<Warehouse> Warehouses { get; } = null!;

    public Task<bool> AnyWarehousesAsync(CancellationToken ct) => Warehouses.AnyAsync(ct);

    public Task SaveChangesAsync(CancellationToken ct) => Task.CompletedTask;
}

internal sealed class Seeder
{
    private readonly SeedContext context;
    private readonly SeedData seedData;

    public Seeder(SeedContext context, SeedData seedData)
    {
        this.context = context;
        this.seedData = seedData;
    }

// snippet:begin
public async Task SeedAsync(CancellationToken ct)
{
    if (await context.Warehouses.AnyAsync(ct).ConfigureAwait(false)) return;
    context.Warehouses.AddRange(seedData.Warehouses);
    await context.SaveChangesAsync(ct).ConfigureAwait(false);
}
// snippet:end

}
