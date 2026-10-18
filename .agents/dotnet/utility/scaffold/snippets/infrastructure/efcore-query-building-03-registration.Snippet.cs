namespace SnippetFixtures.EfQueryPatterns;

using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

// snippet:begin
public static class OrderServices
{
    public static IServiceCollection AddOrderQueries(
        this IServiceCollection services, Action<DbContextOptionsBuilder> configureDatabase)
    {
        services.AddSingleton(TimeProvider.System);
        services.AddSingleton<OrderQueryBuilder>();
        services.AddDbContext<OrderDbContext>(configureDatabase);
        services.AddScoped<OrderRepository>();
        return services;
    }
}
// snippet:end
