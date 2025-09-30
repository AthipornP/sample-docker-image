using System.Text.Json;

namespace Dotnet8Api.Auth;

// Middleware นี้ทำหน้าที่ตรวจสอบ JWT จาก Keycloak ก่อนให้คำขอเข้าสู่ API หลัก
public sealed class KeycloakJwtMiddleware
{
    public const string TokenPayloadKey = "KeycloakTokenPayload";

    private readonly RequestDelegate _next;
    private readonly ILogger<KeycloakJwtMiddleware> _logger;
    private readonly KeycloakJwtValidator _validator;

    private static readonly string[] _anonymousPrefixes =
    {
        "/api/health",
        "/health",
        "/_health"
    };

    public KeycloakJwtMiddleware(RequestDelegate next, ILogger<KeycloakJwtMiddleware> logger, KeycloakJwtValidator validator)
    {
        _next = next;
        _logger = logger;
        _validator = validator;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // อนุญาตให้คำขอแบบ OPTIONS (preflight) ผ่านไปโดยไม่ตรวจ JWT เพื่อรองรับ CORS
        if (HttpMethods.IsOptions(context.Request.Method))
        {
            await _next(context);
            return;
        }

        // ตรวจสอบว่าเส้นทางนี้อยู่ในรายการยกเว้นที่ไม่ต้องตรวจสอบสิทธิ์หรือไม่
        if (ShouldBypass(context.Request.Path))
        {
            await _next(context);
            return;
        }

        // ดึงค่า Authorization header แล้วตรวจว่ามี Bearer token หรือไม่
        var authHeader = context.Request.Headers.Authorization.FirstOrDefault();
        if (string.IsNullOrWhiteSpace(authHeader) || !authHeader.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
        {
            await WriteUnauthorizedAsync(context, "Missing bearer token.");
            return;
        }

        // ตัดคำว่า "Bearer" ออกแล้วเก็บเฉพาะตัว token จริง ๆ
        var token = authHeader["Bearer ".Length..].Trim();
        if (string.IsNullOrEmpty(token))
        {
            await WriteUnauthorizedAsync(context, "Empty bearer token.");
            return;
        }

        try
        {
            // ส่ง token ไปให้ตัว Validator ตรวจสอบลายเซ็น วันหมดอายุ และข้อมูลอื่น ๆ
            var result = await _validator.ValidateAsync(token, context.RequestAborted).ConfigureAwait(false);

            // หากผ่านการตรวจสอบ ให้ผูก ClaimsPrincipal กับ HttpContext.User เพื่อใช้ต่อใน endpoint
            context.User = result.Principal;

            // เก็บ payload ดิบไว้ใน context.Items เผื่อ endpoint ภายหลังต้องใช้ข้อมูล claim เพิ่มเติม
            context.Items[TokenPayloadKey] = result.Payload;
            await _next(context);
        }
        catch (Exception ex)
        {
            // ถ้า JWT ตรวจไม่ผ่าน ให้คืน 401 พร้อมรายละเอียด และบันทึก log ไว้
            _logger.LogWarning(ex, "JWT validation failed.");
            await WriteUnauthorizedAsync(context, ex.Message);
        }
    }

    private static bool ShouldBypass(PathString path)
    {
        // ถ้าไม่มี path ให้ถือว่ายกเว้นไปเลย (เช่น คำขอวิ่งมาที่ root)
        if (!path.HasValue)
        {
            return true;
        }

        foreach (var prefix in _anonymousPrefixes)
        {
            // ถ้า path ขึ้นต้นด้วย prefix ที่อนุญาต ก็ผ่านโดยไม่ต้องตรวจ JWT
            if (path.StartsWithSegments(prefix, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    private static Task WriteUnauthorizedAsync(HttpContext context, string message)
    {
        // สร้าง response แบบ JSON ตอบกลับให้ client ทราบว่าไม่ผ่านการตรวจสอบสิทธิ์
        context.Response.StatusCode = StatusCodes.Status401Unauthorized;
        context.Response.ContentType = "application/json";
        var payload = JsonSerializer.Serialize(new
        {
            error = "Unauthorized",
            detail = message
        });
        return context.Response.WriteAsync(payload);
    }
}
