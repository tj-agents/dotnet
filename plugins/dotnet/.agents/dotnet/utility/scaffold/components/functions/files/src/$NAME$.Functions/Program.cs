using Microsoft.Azure.Functions.Worker.Builder;
using Microsoft.Extensions.Hosting;
$FUNCTIONS_INFRASTRUCTURE_USING$
$FUNCTIONS_TELEMETRY_USING$

var builder = FunctionsApplication.CreateBuilder(args);
$FUNCTIONS_INFRASTRUCTURE_SETUP$
$FUNCTIONS_TELEMETRY_REGISTRATION$

var host = builder.Build();
host.Run();
