namespace SnippetFixtures.EfQueryPatterns;

using System.Linq.Expressions;

// snippet:begin
public sealed class ReadyOrdersSpecification : PredicateSpecification<Order>
{
    private readonly Guid[] ids;
    private readonly DateTimeOffset asOf;

    public ReadyOrdersSpecification(IEnumerable<Guid> ids, DateTimeOffset asOf)
    {
        this.ids = ids.ToArray();
        this.asOf = asOf;
    }

    protected override Expression<Func<Order, bool>> Predicate =>
        order => ids.Contains(order.Id) && order.ReadyAt <= asOf;
}
// snippet:end
