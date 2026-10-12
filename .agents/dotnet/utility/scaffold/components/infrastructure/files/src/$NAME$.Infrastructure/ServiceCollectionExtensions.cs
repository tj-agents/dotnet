$INFRASTRUCTURE_USINGS$
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace $NAME$.Infrastructure;

public static class ServiceCollectionExtensions
{
    extension(IServiceCollection services)
    {
        public IServiceCollection AddInfrastructure(IConfiguration configuration)
        {
$INFRASTRUCTURE_REGISTRATIONS$

            return services;
        }
    }
}
