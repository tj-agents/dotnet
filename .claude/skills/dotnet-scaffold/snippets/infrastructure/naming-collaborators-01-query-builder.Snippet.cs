namespace SnippetFixtures.NamingCollaborators01;

using SnippetFixtures.EfQueryPatterns;

// snippet:begin
public interface IOrderQueryBuilder
{
    IQueryable<Order> Build(IQueryable<Order> source, ReadyOrdersParameters parameters);
}
// snippet:end
