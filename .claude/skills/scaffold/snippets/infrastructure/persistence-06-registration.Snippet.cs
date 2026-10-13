namespace SnippetFixtures.Persistence06;

using Microsoft.Extensions.DependencyInjection;

internal sealed class OrderDbContext : Shared.IDbContext;
internal interface IUnitOfWork : DataAccess.Application.IUnitOfWork<OrderDbContext>;
internal sealed class UnitOfWork(OrderDbContext context) : DataAccess.Infrastructure.UnitOfWork<OrderDbContext>(context), IUnitOfWork;
internal interface IUnitOfWorkBehavior;
internal sealed class UnitOfWorkBehavior : IUnitOfWorkBehavior;

internal static class Example
{
    public static void Register(IServiceCollection services)
    {
// snippet:begin
services.AddScoped<IUnitOfWork, UnitOfWork>();
services.AddScoped<IUnitOfWorkBehavior, UnitOfWorkBehavior>();
// snippet:end

    }
}
