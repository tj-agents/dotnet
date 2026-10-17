namespace SnippetFixtures.Mapping01;

internal sealed class ShipmentEntity
{
    public Guid Id { get; init; }
    public string TrackingReference { get; init; } = null!;
}

internal sealed record Shipment(Guid Id, string TrackingReference);

// snippet:begin
internal static class ShipmentMappers
{
    extension(ShipmentEntity entity)
    {
        public Shipment ToShipment() => new(entity.Id, entity.TrackingReference);
    }
}
// snippet:end
