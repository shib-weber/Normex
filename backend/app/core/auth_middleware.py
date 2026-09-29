from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from app.core.config import settings

PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Browser CORS preflight requests must always pass through.
        if request.method == "OPTIONS" or path in PUBLIC_PATHS:
            return await call_next(request)

        # Protect all NORMEX API endpoints except explicitly public paths.
        if path.startswith("/api/v1/"):
            authorization = request.headers.get("Authorization", "")
            if not authorization.startswith("Bearer "):
                return JSONResponse(
                    {"detail": "Official authentication required"},
                    status_code=401,
                )

            token = authorization.split(" ", 1)[1].strip()
            try:
                jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=["HS256"],
                )
            except Exception:
                return JSONResponse(
                    {"detail": "Invalid or expired official session"},
                    status_code=401,
                )

        return await call_next(request)

# Backward-compatible name for code that imports auth_middleware.
auth_middleware = AuthMiddleware
