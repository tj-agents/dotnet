using Microsoft.Extensions.Hosting;
$WORKER_INFRASTRUCTURE_USING$
$WORKER_TELEMETRY_USING$

var builder = Host.CreateApplicationBuilder(args);
$WORKER_INFRASTRUCTURE_SETUP$
$WORKER_TELEMETRY_REGISTRATION$

await builder.Build().RunAsync().ConfigureAwait(false);
