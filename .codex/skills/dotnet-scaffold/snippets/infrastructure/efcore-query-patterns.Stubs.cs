using System.Linq.Expressions;
using Microsoft.EntityFrameworkCore;

namespace SnippetFixtures.EfQueryPatterns;

public interface IPredicateSpecification<TEntity>
{
    Expression<Func<TEntity, bool>> ToExpression();
}

public abstract class PredicateSpecification<TEntity> : IPredicateSpecification<TEntity>
{
    protected abstract Expression<Func<TEntity, bool>> Predicate { get; }

    public Expression<Func<TEntity, bool>> ToExpression() => Predicate;
}

public sealed class Order
{
    public Guid Id { get; init; }
    public DateTimeOffset ReadyAt { get; init; }
}

public sealed class OrderDbContext(DbContextOptions<OrderDbContext> options) : DbContext(options)
{
    public DbSet<Order> Orders => base.Set<Order>();
}
