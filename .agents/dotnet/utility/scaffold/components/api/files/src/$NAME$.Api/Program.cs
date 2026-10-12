$INFRASTRUCTURE_USING$
$API_USINGS$

var builder = WebApplication.CreateBuilder(args);
$INFRASTRUCTURE_SETUP$
$API_SERVICE_REGISTRATIONS$

var app = builder.Build();
$API_PIPELINE$

app.Run();
