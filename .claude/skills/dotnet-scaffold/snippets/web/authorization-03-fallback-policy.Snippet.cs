namespace SnippetFixtures.Authorization03;

using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.DependencyInjection;

internal static class AuthorizationRegistration
{
    public static void Register(IServiceCollection services)
    {
// snippet:begin
services.AddAuthorizationBuilder()
    .SetFallbackPolicy(new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build());
// snippet:end

    }
}
