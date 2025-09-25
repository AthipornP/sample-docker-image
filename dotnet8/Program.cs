var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => Results.Content("<h1>.NET 8 Sample App</h1><p>Running in container</p><p><a href='http://localhost:3000' target='_top' style='display:inline-block;padding:10px 16px;background:#1976d2;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;'>Back to Portal</a></p>", "text/html"));

app.Run();
