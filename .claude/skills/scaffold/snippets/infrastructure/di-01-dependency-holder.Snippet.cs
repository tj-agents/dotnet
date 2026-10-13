namespace SnippetFixtures.DependencyInjection01;

internal sealed class ReserveStockStep : IReserveStep;
internal sealed class ChargeCardStep : IChargeStep;
internal sealed class DispatchStep : IDispatchStep;
internal interface IReserveStep;
internal interface IChargeStep;
internal interface IDispatchStep;
internal interface IFulfilmentFlow;

// snippet:begin
internal sealed class StandardFulfilmentFlow : IFulfilmentFlow
{
    public StandardFulfilmentFlow(
        ReserveStockStep reserveStockStep,
        ChargeCardStep chargeCardStep,
        DispatchStep dispatchStep)
    {
        Reserve = reserveStockStep;
        Charge = chargeCardStep;
        Dispatch = dispatchStep;
    }

    public IReserveStep Reserve { get; }
    public IChargeStep Charge { get; }
    public IDispatchStep Dispatch { get; }
}
// snippet:end
