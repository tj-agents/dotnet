namespace SnippetFixtures.KeyedStrategies01;

using Microsoft.Extensions.DependencyInjection;

internal enum FulfilmentMode { Digital, Collection, Courier, Freight }

// snippet:begin
internal interface IFulfilmentStrategyFactory<TStrategy>
    where TStrategy : class
{
    TStrategy Create(FulfilmentMode mode);
}

internal sealed class FulfilmentStrategyFactory<TStrategy> : IFulfilmentStrategyFactory<TStrategy>
    where TStrategy : class
{
    private readonly IKeyedServiceProvider services;

    public FulfilmentStrategyFactory(IKeyedServiceProvider services)
    {
        this.services = services;
    }

    public TStrategy Create(FulfilmentMode mode) =>
        services.GetRequiredKeyedService<TStrategy>(mode);
}
// snippet:end
