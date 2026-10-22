namespace SnippetFixtures.MicroserviceBoundaries01;

using Grpc.Net.ClientFactory;
using Microsoft.Extensions.DependencyInjection;

internal static class Example
{
    public static void Register(IServiceCollection services)
    {
// snippet:begin
services.AddGrpcClient<Proto.Escrow.EscrowClient>(options => options.Address = new Uri("https://escrow"));
// snippet:end

    }
}
