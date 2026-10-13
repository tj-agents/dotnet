namespace SnippetFixtures.DomainEvents03;

using Microsoft.Extensions.DependencyInjection;

internal sealed record OrderCancelledDomainEvent(object Order) : IDomainEvent;
internal sealed class OrderCancelledDomainEventHandler : IDomainEventHandler<OrderCancelledDomainEvent>
{
    public Task HandleAsync(OrderCancelledDomainEvent domainEvent, CancellationToken ct = default) => Task.CompletedTask;
}

internal static class Registration
{
    public static void Register(IServiceCollection services)
    {
// snippet:begin
services.AddScoped<IDomainEventHandler<OrderCancelledDomainEvent>, OrderCancelledDomainEventHandler>();
// snippet:end

    }
}
