using Grpc.Core;

namespace Proto;

internal static class Escrow
{
    public sealed class EscrowClient(CallInvoker invoker) : ClientBase<EscrowClient>(invoker);
}
