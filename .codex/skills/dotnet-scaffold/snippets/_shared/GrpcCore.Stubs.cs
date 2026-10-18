namespace Grpc.Core;

public abstract class CallInvoker;

public abstract class ClientBase<T>
    where T : ClientBase<T>
{
    protected ClientBase(CallInvoker invoker) { }
}

public sealed class Metadata
{
    public void Add(string key, string value) { }
}

public sealed class AuthInterceptorContext;
