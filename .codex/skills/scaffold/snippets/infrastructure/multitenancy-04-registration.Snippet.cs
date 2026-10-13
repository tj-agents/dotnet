namespace SnippetFixtures.Multitenancy04;

using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

internal static class Configuration
{
    extension(DbContextOptionsBuilder builder)
    {
        public DbContextOptionsBuilder UseOrdersDb(object configuration) => builder;
    }
}
internal sealed class OrderDbContext(DbContextOptions<OrderDbContext> options) : DbContext(options);
internal interface IOrderReadDbContext;
internal sealed class OrderReadDbContext(DbContextOptions<OrderReadDbContext> options) : DbContext(options), IOrderReadDbContext;
internal sealed class AuditInterceptor : Microsoft.EntityFrameworkCore.Diagnostics.SaveChangesInterceptor;
internal sealed class TenantInterceptor : Microsoft.EntityFrameworkCore.Diagnostics.SaveChangesInterceptor;
internal interface IDomainEventDispatchInterceptor : Microsoft.EntityFrameworkCore.Diagnostics.IInterceptor;
internal sealed class DomainEventDispatchInterceptor : Microsoft.EntityFrameworkCore.Diagnostics.SaveChangesInterceptor, IDomainEventDispatchInterceptor;
internal static class SeedingExtensions
{
    extension(DbContextOptionsBuilder builder)
    {
        public DbContextOptionsBuilder UseSeedingSupport(IServiceProvider sp) => builder;
    }
}

internal static class Example
{
    public static void Register(IServiceCollection services, object configuration)
    {
// snippet:begin
services.AddDbContext<OrderDbContext>((sp, options) =>
    options.UseOrdersDb(configuration)
        .AddInterceptors(
            sp.GetRequiredService<AuditInterceptor>(),
            sp.GetRequiredService<TenantInterceptor>(),
            sp.GetRequiredService<IDomainEventDispatchInterceptor>())
        .UseSeedingSupport(sp));

services.AddDbContext<OrderReadDbContext>(options =>
    options.UseOrdersDb(configuration)
        .UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking));
services.AddScoped<IOrderReadDbContext>(sp => sp.GetRequiredService<OrderReadDbContext>());
// snippet:end

    }
}
