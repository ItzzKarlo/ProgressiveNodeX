var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => new
{
    name = "dotnet-webapi",
    status = "ok",
    generatedBy = "ProgressiveNodeX"
});

app.MapGet("/health", () => new { ok = true });

app.Run();