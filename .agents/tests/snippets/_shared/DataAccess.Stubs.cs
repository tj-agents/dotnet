using Microsoft.EntityFrameworkCore;

namespace Shared;

public interface IDbContext;

public interface IReadDbContext : IDbContext
{
    IQueryable<TEntity> Query<TEntity>() where TEntity : class;
}

public interface IWriteDbContext : IDbContext;

public interface IReadRepository<TEntity, TKey> where TEntity : class;

public interface IWriteRepository<TEntity> where TEntity : class
{
    Task InsertAsync(TEntity entity, CancellationToken ct = default);
    Task AddAsync(TEntity entity, CancellationToken ct = default);
    Task SaveChangesAsync(CancellationToken ct = default);
}

public interface IRepository<TEntity, TKey> : IReadRepository<TEntity, TKey>, IWriteRepository<TEntity>
    where TEntity : class;

public abstract class ReadRepository<TEntity, TKey>(IReadDbContext context) : IReadRepository<TEntity, TKey>
    where TEntity : class
{
    protected IReadDbContext Context { get; } = context;
}

public abstract class WriteRepository<TEntity>(IWriteDbContext context) : IWriteRepository<TEntity>
    where TEntity : class
{
    protected IWriteDbContext Context { get; } = context;

    public Task InsertAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task AddAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task SaveChangesAsync(CancellationToken ct = default) => Task.CompletedTask;
}

public abstract class Repository<TEntity, TKey>(IDbContext context) : IRepository<TEntity, TKey>
    where TEntity : class
{
    protected IDbContext Context { get; } = context;

    public Task InsertAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task AddAsync(TEntity entity, CancellationToken ct = default) => Task.CompletedTask;
    public Task SaveChangesAsync(CancellationToken ct = default) => Task.CompletedTask;
}

public interface ITenantContext
{
    Guid TenantId { get; }
}

public abstract class TenantScopedDbContext(
    object options, object provider, ITenantContext tenantContext, string schema) : DbContext
{
    protected virtual void ApplyTenantFilters(ModelBuilder modelBuilder) { }
}

public abstract class ReadDbContext(object options, object provider, string schema) : DbContext
{
    public IQueryable<TEntity> Query<TEntity>() where TEntity : class => Set<TEntity>();
}

public abstract class PrivilegedDbContext(object options, object provider, string schema) : DbContext;

public interface IPagination<out T>
{
    IReadOnlyList<T> Data { get; }
    int TotalCount { get; }
    int PageNumber { get; }
    int PageSize { get; }

    IPagination<TNext> Map<TNext>(Func<T, TNext> map);
}
