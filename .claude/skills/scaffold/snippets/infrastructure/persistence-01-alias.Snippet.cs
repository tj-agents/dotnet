namespace SnippetFixtures.Persistence01;

internal interface IGuidEntity { Guid Id { get; } }
internal sealed class OrderDbContext : Shared.IDbContext;

// snippet:begin
internal abstract class Repository<TEntity>(OrderDbContext context)
    : Repository<TEntity, Guid>(context)
    where TEntity : class, IGuidEntity;
// snippet:end
