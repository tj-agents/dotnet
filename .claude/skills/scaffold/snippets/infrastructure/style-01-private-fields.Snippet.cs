namespace SnippetFixtures.Style01;

internal sealed class OrderDbContext;

#pragma warning disable CS0169, CS8618

internal sealed class OrderService
{
// snippet:begin
// CORRECT — "context" shadows the field, so this. disambiguates it
private readonly OrderDbContext context;

public OrderService(OrderDbContext context)
{
    this.context = context;
}

// WRONG
private readonly OrderDbContext _context;
// snippet:end

}

#pragma warning restore CS0169, CS8618
