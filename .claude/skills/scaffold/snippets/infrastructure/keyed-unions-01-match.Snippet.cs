namespace SnippetFixtures.KeyedUnions01;

using Dunet;

public enum FulfilmentMode { Digital, Collection, Courier, Freight }
public sealed record Parcel;
public sealed record Order(Guid Id)
{
    public FulfilmentMode Mode { get; init; }
}
public sealed record Address;
internal sealed record FulfilmentRequest(Address Address);
public interface IFulfil { object Fulfil(Parcel parcel, Order order); }
public interface IFulfilToAddress { object Fulfil(Parcel parcel, Order order, Address address); }

[Union]
public abstract partial record Fulfilment
{
    public partial record Fulfil(IFulfil Value);
    public partial record FulfilToAddress(IFulfilToAddress Value);
}

internal interface IFulfilmentFactory { Fulfilment Create(FulfilmentMode mode); }

internal static class Example
{
    public static object Handle(IFulfilmentFactory fulfilmentFactory, Parcel parcel, Order order, FulfilmentRequest request)
    {
// snippet:begin
var result = fulfilmentFactory.Create(order.Mode) switch
{
    Fulfilment.Fulfil(var fulfil) => fulfil.Fulfil(parcel, order),
    Fulfilment.FulfilToAddress(var fulfil) => fulfil.Fulfil(parcel, order, request.Address)
};
// snippet:end

        return result;
    }
}
