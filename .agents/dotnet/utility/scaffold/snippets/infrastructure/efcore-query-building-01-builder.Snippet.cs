namespace SnippetFixtures.EfQueryPatterns;

// snippet:begin
public sealed record ReadyOrdersParameters(IReadOnlyCollection<Guid> Ids);

public sealed class OrderQueryBuilder
{
    private readonly TimeProvider timeProvider;

    public OrderQueryBuilder(TimeProvider timeProvider)
    {
        this.timeProvider = timeProvider;
    }

    public IQueryable<Order> Build(IQueryable<Order> source, ReadyOrdersParameters parameters)
    {
        var asOf = timeProvider.GetUtcNow();
        IPredicateSpecification<Order> specification = new ReadyOrdersSpecification(parameters.Ids, asOf);

        return source.Where(specification.ToExpression())
            .OrderBy(order => order.ReadyAt)
            .ThenBy(order => order.Id);
    }
}
// snippet:end
