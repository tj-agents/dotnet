$INFRASTRUCTURE_USING$

var builder = WebApplication.CreateBuilder(args);
$INFRASTRUCTURE_SETUP$

var app = builder.Build();

app.Run();
