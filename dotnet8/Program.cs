var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => Results.Content("<h1>.NET 8 Sample App</h1><p>Running in container</p>", "text/html"));

app.Run();
