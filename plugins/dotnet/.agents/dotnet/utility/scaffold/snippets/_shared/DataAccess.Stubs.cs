using Microsoft.EntityFrameworkCore;

namespace Shared;

public interface IDbContext;

public interface IReadDbContext
{
    IQueryable<TEntity> Query<TEntity>() where TEntity : class;
}

public interface IWriteDbContext;

public interface IReadRepository<TEntity, TKey> where TEntity : class;

public interface IWriteRepository<TEntity> where TEntity : class
{
    Task InsertAsync(TEntity entity, CancellationToken ct = default);
    Task AddAsync(TEntity entity, CancellationToken ct = default);
    Task SaveChangesAsync(CancellationToken ct = default);
}

public interface IRepository<TEntity, TKey> : IReadRepository<TEntity, TKey>, IWriteRepository<TEntity>
    where TEntity : class;

public abstract class ReadRepository<TEntity, TKey> : IReadRepository<TEntity, TKey>
    where TEntity : class
{
    private readonly IReadDbContext context;

    protected ReadRepository(IReadDbContext context)
    {
        this.context = context;
    }

    protected IReadDbContext Context => context;
}

public abstract class WriteRepository<TEntity> : IWriteRepository<TEntity>
    where TEntity : class
{
    private readonly IWriteDbContext context;

    protected WriteRepository(IWriteDbContext context)
    {
        this.context = context;
    }

    protected IWriteDbContext Context => context;

    public Task InsertAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task AddAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task SaveChangesAsync(CancellationToken ct = default) => Task.CompletedTask;
}

public abstract class Repository<TEntity, TKey> : IRepository<TEntity, TKey>
    where TEntity : class
{
    private readonly IDbContext context;

    protected Repository(IDbContext context)
    {
        this.context = context;
    }

    protected IDbContext Context => context;

    public Task InsertAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task AddAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task SaveChangesAsync(CancellationToken ct = default) => Task.CompletedTask;
}

public interface ITenantContext
{
    Guid TenantId { get; }
}

public abstract class TenantScopedDbContext(
    object options, object provider, ITenantContext tenantContext, string schema) : DbContext, IDbContext
{
    protected virtual void ApplyTenantFilters(ModelBuilder modelBuilder) { }
}

public abstract class ReadDbContext(object options, object provider, string schema) : DbContext, IReadDbContext
{
    public IQueryable<TEntity> Query<TEntity>() where TEntity : class => base.Set<TEntity>();

    public override int SaveChanges() => throw new InvalidOperationException();
    public override Task<int> SaveChangesAsync(CancellationToken ct = default) =>
        throw new InvalidOperationException();
}

public abstract class PrivilegedDbContext(object options, object provider, string schema) : DbContext, IDbContext;

public interface IPagination<out T>
{
    IReadOnlyList<T> Data { get; }
    int TotalCount { get; }
    int PageNumber { get; }
    int PageSize { get; }

    IPagination<TNext> Map<TNext>(Func<T, TNext> map);
}
