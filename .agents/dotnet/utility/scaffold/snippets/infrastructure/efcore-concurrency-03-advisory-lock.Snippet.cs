namespace SnippetFixtures.Concurrency03;

using Microsoft.EntityFrameworkCore;

internal sealed class InvoiceRepository
{
    private readonly DbContext context;

    public InvoiceRepository(DbContext context) => this.context = context;

// snippet:begin
public Task AcquireInvoiceNumberLockAsync(Guid tenantId, CancellationToken ct = default) =>
    context.Database.ExecuteSqlAsync($"SELECT pg_advisory_xact_lock(hashtext({tenantId.ToString()}))", ct);
// snippet:end

}
