namespace SnippetFixtures.NamingCollaborators01;

// snippet:begin
public interface IIntegrationEventPublisher
{
    Task PublishAsync<TEvent>(TEvent integrationEvent, CancellationToken ct = default)
        where TEvent : IIntegrationEvent;
}
// snippet:end
