using System.Data.Common;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
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
    private readonly $FIXTURE_CONTAINER_TYPE$ container = $FIXTURE_CONTAINER_CREATION$;
    private Respawner? respawner;

    public HttpClient Client { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        await this.container.StartAsync();
        this.Client = this.CreateClient();
    }

    public async Task ResetAsync()
    {
        await using DbConnection connection = $FIXTURE_CONNECTION_CREATION$;
        await connection.OpenAsync();
        this.respawner ??= await Respawner.CreateAsync(
            connection,
            new RespawnerOptions { DbAdapter = $FIXTURE_DB_ADAPTER$ });
        await this.respawner.ResetAsync(connection);
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
        await this.container.DisposeAsync();
        this.Dispose();
    }
$FIXTURE_DAPPER_FACTORY$
$FIXTURE_AUTH_HANDLER$
}
