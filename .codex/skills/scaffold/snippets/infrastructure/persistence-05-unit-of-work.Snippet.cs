namespace SnippetFixtures.Persistence05;

internal sealed class OrderDbContext : Shared.IDbContext;

// snippet:begin
internal interface IUnitOfWork : DataAccess.Application.IUnitOfWork<OrderDbContext>;

internal sealed class UnitOfWork(OrderDbContext context)
    : DataAccess.Infrastructure.UnitOfWork<OrderDbContext>(context), IUnitOfWork;
// snippet:end
