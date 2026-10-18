namespace Shared;

public static class GrpcClientServiceCollectionExtensions
{
    extension(Microsoft.Extensions.DependencyInjection.IServiceCollection services)
    {
        public Grpc.Net.ClientFactory.GrpcClientBuilder<TClient> AddGrpcClient<TClient>(
            Action<Grpc.Net.ClientFactory.GrpcClientFactoryOptions> configure)
            where TClient : class =>
            new();
    }
}
