namespace SnippetFixtures.MicroserviceBoundaries01;

using Azure.Messaging.ServiceBus;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

internal sealed record OrderPlacedEvent : IIntegrationEvent;

internal static partial class Log02
{
    [LoggerMessage(Level = LogLevel.Error, Message = "Subscription {EntityPath} processing failed")]
    internal static partial void SubscriptionProcessingFailed(this ILogger logger, string entityPath, Exception exception);
}

// snippet:begin
internal sealed class OrderEventsProcessor : BackgroundService
{
    private readonly ServiceBusProcessor processor;
    private readonly IServiceScopeFactory scopeFactory;
    private readonly ILogger<OrderEventsProcessor> logger;

    public OrderEventsProcessor(
        ServiceBusProcessor processor,
        IServiceScopeFactory scopeFactory,
        ILogger<OrderEventsProcessor> logger)
    {
        this.processor = processor;
        this.scopeFactory = scopeFactory;
        this.logger = logger;
        processor.ProcessMessageAsync += HandleMessageAsync;
        processor.ProcessErrorAsync += HandleErrorAsync;
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken) =>
        processor.StartProcessingAsync(stoppingToken);

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        await processor.StopProcessingAsync(cancellationToken).ConfigureAwait(false);
        await base.StopAsync(cancellationToken).ConfigureAwait(false);
    }

    private async Task HandleMessageAsync(ProcessMessageEventArgs args)
    {
        var integrationEvent = args.Message.Body.ToObjectFromJson<OrderPlacedEvent>();

        var scope = scopeFactory.CreateAsyncScope();
        await using (scope.ConfigureAwait(false))
        {
            var handler = scope.ServiceProvider.GetRequiredService<IIntegrationEventHandler<OrderPlacedEvent>>();
            await handler.HandleAsync(integrationEvent, args.CancellationToken).ConfigureAwait(false);
        }

        await args.CompleteMessageAsync(args.Message, args.CancellationToken).ConfigureAwait(false);
    }

    private Task HandleErrorAsync(ProcessErrorEventArgs args)
    {
        logger.SubscriptionProcessingFailed(args.EntityPath, args.Exception);
        return Task.CompletedTask;
    }
}
// snippet:end
