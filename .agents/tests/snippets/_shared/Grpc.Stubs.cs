namespace Grpc.Core
{
    public class CallInvoker;

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
}

namespace Grpc.Net.ClientFactory
{
    public sealed class GrpcClientFactoryOptions
    {
        public Uri Address { get; set; } = new("http://localhost");
    }

    public sealed class GrpcClientBuilder<TClient>
    {
        public GrpcClientBuilder<TClient> AddCallCredentials(
            Func<Grpc.Core.AuthInterceptorContext, Grpc.Core.Metadata, IServiceProvider, Task> interceptor) => this;
    }
}

public static class GrpcClientServiceCollectionExtensions
{
    public static Grpc.Net.ClientFactory.GrpcClientBuilder<TClient> AddGrpcClient<TClient>(
        this Microsoft.Extensions.DependencyInjection.IServiceCollection services,
        Action<Grpc.Net.ClientFactory.GrpcClientFactoryOptions> configure)
        where TClient : class =>
        new();
}
