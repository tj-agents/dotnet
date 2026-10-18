namespace SnippetFixtures.KeyedUnions02;

internal enum FulfilmentMode { Digital, Collection, Courier, Freight }
internal sealed record Parcel;
internal sealed record Order(Guid Id);
internal sealed record Address;
internal interface IFulfil;
internal interface IFulfilToAddress;
internal sealed class DigitalFulfil : IFulfil;
internal sealed class CollectionFulfil : IFulfil;
internal sealed class CourierFulfil : IFulfilToAddress;
internal abstract record Fulfilment
{
    public sealed record Fulfil(IFulfil Value) : Fulfilment;
    public sealed record FulfilToAddress(IFulfilToAddress Value) : Fulfilment;
}

internal sealed class UnionCaseBuilder<TUnion>
{
    public UnionCaseBuilder<TUnion> Case<TInterface>(Func<TInterface, TUnion> wrap) => this;
    public UnionCaseBuilder<TUnion> Use<TImplementation>(params FulfilmentMode[] modes) => this;
}

internal static class Example
{
    public static void Register(UnionCaseBuilder<Fulfilment> union)
    {
// snippet:begin
union.Case<IFulfil>(fulfil => new Fulfilment.Fulfil(fulfil))
    .Use<DigitalFulfil>(FulfilmentMode.Digital)
    .Use<CollectionFulfil>(FulfilmentMode.Collection);

union.Case<IFulfilToAddress>(fulfil => new Fulfilment.FulfilToAddress(fulfil))
    .Use<CourierFulfil>(FulfilmentMode.Courier, FulfilmentMode.Freight);
// snippet:end

    }
}
