namespace SnippetFixtures.KeyedStrategies04;

// snippet:begin
public abstract class Fulfilment
{
    public abstract bool RequiresTracking { get; }
}

public sealed class CourierFulfilment : Fulfilment
{
    public string TrackingNumber { get; private set; } = null!;

    public override bool RequiresTracking => true;
}
// snippet:end
