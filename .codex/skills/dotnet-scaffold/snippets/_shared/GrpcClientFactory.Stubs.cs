namespace Grpc.Net.ClientFactory;

public sealed class GrpcClientFactoryOptions
{
    public Uri Address { get; set; } = new("http://localhost");
}

public sealed class GrpcClientBuilder<TClient>
{
    public GrpcClientBuilder<TClient> AddCallCredentials(
        Func<Grpc.Core.AuthInterceptorContext, Grpc.Core.Metadata, IServiceProvider, Task> interceptor) => this;
}
