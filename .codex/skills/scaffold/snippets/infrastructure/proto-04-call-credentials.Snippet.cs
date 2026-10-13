namespace SnippetFixtures.Proto04;

using Grpc.Core;
using Grpc.Net.ClientFactory;
using Microsoft.Extensions.DependencyInjection;

internal interface ITokenService { Task<string> GetTokenAsync(string scope); }

internal static class Example
{
    public static void Register(IServiceCollection services, string address)
    {
// snippet:begin
services.AddGrpcClient<Proto.Escrow.EscrowClient>(o => o.Address = new Uri(address))
    .AddCallCredentials(async (_, metadata, sp) =>
    {
        var token = await sp.GetRequiredService<ITokenService>().GetTokenAsync("payments:write").ConfigureAwait(false);
        metadata.Add("Authorization", $"Bearer {token}");
    });
// snippet:end

    }
}
