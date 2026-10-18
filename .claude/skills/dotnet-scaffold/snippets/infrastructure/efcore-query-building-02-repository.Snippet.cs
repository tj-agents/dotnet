namespace SnippetFixtures.EfQueryPatterns;

using Microsoft.EntityFrameworkCore;

// snippet:begin
public sealed class OrderRepository
{
    private readonly OrderDbContext context;
    private readonly OrderQueryBuilder queryBuilder;

    public OrderRepository(OrderDbContext context, OrderQueryBuilder queryBuilder)
    {
        this.context = context;
        this.queryBuilder = queryBuilder;
    }

    public async Task<IReadOnlyList<Order>> GetReadyAsync(
        ReadyOrdersParameters parameters, CancellationToken ct = default) =>
        await queryBuilder.Build(context.Orders.AsNoTracking(), parameters)
            .ToListAsync(ct).ConfigureAwait(false);
}
// snippet:end
