namespace DataAccess.Application
{
    public interface IUnitOfWork<TContext>;
}

namespace DataAccess.Infrastructure
{
    public abstract class UnitOfWork<TContext>(TContext context);
}
