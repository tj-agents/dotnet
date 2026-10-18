$INFRASTRUCTURE_USING$
$WEB_USINGS$

var builder = WebApplication.CreateBuilder(args);
$INFRASTRUCTURE_SETUP$
$WEB_SERVICE_REGISTRATIONS$

var app = builder.Build();
$WEB_PIPELINE$

app.Run();
$WEB_PROGRAM_DECLARATIONS$
