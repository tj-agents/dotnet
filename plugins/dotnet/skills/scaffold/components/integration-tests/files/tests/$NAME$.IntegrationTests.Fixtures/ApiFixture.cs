using System.Data.Common;
using System.Security.Cryptography;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Respawn;
using Xunit;
using $NAME$.Infrastructure;
$FIXTURE_PROVIDER_USING$
$FIXTURE_EF_USING$
$FIXTURE_AUTH_USINGS$

namespace $NAME$.IntegrationTests.Fixtures;

public sealed class ApiFixture : WebApplicationFactory<global::Program>, IAsyncLifetime
{
    private readonly $FIXTURE_CONTAINER_TYPE$ container;
    private Respawner? respawner;

    public HttpClient Client { get; private set; } = null!;

    public ApiFixture()
    {
        this.container = $FIXTURE_CONTAINER_CREATION$;
    }

    public async Task InitializeAsync()
    {
        await this.container.StartAsync().ConfigureAwait(false);
        this.Client = this.CreateClient();
    }

    public async Task ResetAsync()
    {
        DbConnection connection = $FIXTURE_CONNECTION_CREATION$;
        await using (connection.ConfigureAwait(false))
        {
            await connection.OpenAsync().ConfigureAwait(false);
            this.respawner ??= await Respawner.CreateAsync(
                connection,
                new RespawnerOptions { DbAdapter = $FIXTURE_DB_ADAPTER$ }).ConfigureAwait(false);
            await this.respawner.ResetAsync(connection).ConfigureAwait(false);
        }
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureTestServices(services =>
        {
$FIXTURE_SERVICE_CONFIGURATION$
$FIXTURE_AUTH_CONFIGURATION$
        });
    }

    async Task IAsyncLifetime.DisposeAsync()
    {
        await this.container.DisposeAsync().ConfigureAwait(false);
        this.Dispose();
    }

    private static string CreatePassword()
    {
        return "Aa1!" + Convert.ToHexString(RandomNumberGenerator.GetBytes(24));
    }
$FIXTURE_DAPPER_FACTORY$
$FIXTURE_AUTH_HANDLER$
}
