"""
Middleware for SentinelAI: Rate Limiting + Audit Logging.
"""
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from loguru import logger


# --- Rate Limiting ---

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter: 100 requests/minute per user/IP."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip health checks and docs
        path = request.url.path
        if path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        # Identify client by token sub or IP
        client_id = self._get_client_id(request)
        now = time.time()
        window_start = now - 60

        # Clean old entries
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]

        if len(self.requests[client_id]) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Max 100 requests per minute.",
                    "retry_after_seconds": 60,
                },
            )

        self.requests[client_id].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rpm)
        response.headers["X-RateLimit-Remaining"] = str(
            self.rpm - len(self.requests[client_id])
        )
        return response

    def _get_client_id(self, request: Request) -> str:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            # Use first 16 chars of token as identifier
            return f"token:{auth[7:23]}"
        # Fall back to IP
        client = request.client
        return f"ip:{client.host if client else 'unknown'}"


# --- Audit Logging ---

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Automatically logs mutating requests to the audit_logs table."""

    AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    SKIP_PATHS = {"/api/v1/auth/login", "/api/v1/auth/refresh", "/health"}

    async def dispatch(self, request: Request, call_next):
        # Always call next first — never block the response
        response = await call_next(request)

        method = request.method
        path = request.url.path

        # Only audit mutating operations
        if method not in self.AUDITABLE_METHODS:
            return response
        if path in self.SKIP_PATHS:
            return response

        # Log audit in background (don't block response)
        try:
            await self._write_audit_log(request, response)
        except Exception as e:
            logger.error(f"Audit log write failed: {e}")

        return response

    async def _write_audit_log(self, request: Request, response: Response):
        from app.core.database import async_session_factory
        from app.models.analytics import AuditLog
        from app.core.security import decode_token

        # Extract user from token
        user_id = None
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            payload = decode_token(auth[7:])
            if payload:
                user_id = payload.get("sub")

        # Determine action and resource
        method = request.method
        path = request.url.path
        action = self._method_to_action(method)
        resource_type = self._path_to_resource(path)

        status = response.status_code
        description = f"{method} {path} → {status}"

        client = request.client
        ip = client.host if client else "unknown"
        user_agent = request.headers.get("user-agent", "")[:500]

        try:
            async with async_session_factory() as session:
                log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=self._extract_resource_id(path),
                    description=description,
                    ip_address=ip,
                    user_agent=user_agent,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"Audit DB write failed: {e}")

    def _method_to_action(self, method: str) -> str:
        return {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }.get(method, "unknown")

    def _path_to_resource(self, path: str) -> str:
        parts = path.strip("/").split("/")
        # /api/v1/cases/123 → "cases"
        for i, p in enumerate(parts):
            if p == "v1" and i + 1 < len(parts):
                return parts[i + 1]
        return parts[-1] if parts else "unknown"

    def _extract_resource_id(self, path: str) -> str:
        parts = path.strip("/").split("/")
        # Try to find UUID-like segment
        for p in reversed(parts):
            if len(p) >= 32 and "-" in p:
                return p
        return ""
