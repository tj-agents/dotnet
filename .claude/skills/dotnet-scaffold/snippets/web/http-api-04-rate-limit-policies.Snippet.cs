namespace SnippetFixtures.HttpApi04;

using System.Security.Claims;
using System.Threading.RateLimiting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;

internal static class RateLimitPolicies
{
    public const string SignIn = "sign-in";
    public const string BulkExport = "bulk-export";
}

internal static class RateLimitRegistration
{
    public static void Register(
        IServiceCollection services,
        FixedWindowRateLimiterOptions signInWindow,
        FixedWindowRateLimiterOptions bulkExportWindow)
    {
// snippet:begin
services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddPolicy(RateLimitPolicies.SignIn, context =>
        RateLimitPartition.GetFixedWindowLimiter(ClientAddress(context), _ => signInWindow));
    options.AddPolicy(RateLimitPolicies.BulkExport, context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.User.FindFirstValue(ClaimTypes.NameIdentifier) ?? ClientAddress(context),
            _ => bulkExportWindow));
});
// snippet:end

    }

    private static string ClientAddress(HttpContext context) =>
        context.Connection.RemoteIpAddress?.ToString() ?? string.Empty;
}
