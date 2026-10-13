namespace SnippetFixtures.Persistence02;

internal interface IGuidEntity { Guid Id { get; } }
internal sealed class OrderEntity : IGuidEntity { public Guid Id { get; init; } }
internal sealed class OrderDbContext : Shared.IDbContext;
internal abstract class Repository<TEntity> : Repository<TEntity, Guid> where TEntity : class, IGuidEntity
{
    protected Repository(OrderDbContext context) : base(context) { }
}

// snippet:begin
internal interface IOrderRepository : IRepository<OrderEntity, Guid>;

internal sealed class OrderRepository : Repository<OrderEntity>, IOrderRepository
{
    public OrderRepository(OrderDbContext context) : base(context) { }
    // extra finders only — query via the inherited `context`
}
// snippet:end
