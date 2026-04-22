import os
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from auth import auth_router
from chat import chat_router
from config.limiter import limiter
from config.logger import get_logger
from docs import docs_router

logger = get_logger("main")

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth_router)
app.include_router(docs_router)
app.include_router(chat_router)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.perf_counter()
    logger.info(
        "→ REQUEST  | method=%s path=%s client=%s",
        request.method,
        request.url.path,
        request.client.host if request.client else "unknown",
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        elapsed = (time.perf_counter() - start) * 1000
        logger.error(
            "← RESPONSE | method=%s path=%s status=500 duration=%.1fms error=%s",
            request.method,
            request.url.path,
            elapsed,
            exc,
            exc_info=True,
        )
        raise

    elapsed = (time.perf_counter() - start) * 1000
    level = logger.warning if response.status_code >= 400 else logger.info
    level(
        "← RESPONSE | method=%s path=%s status=%d duration=%.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception | method=%s path=%s error=%s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/health")
def health_check():
    return {"message": "Server is running"}


if __name__ == "__main__":
    logger.info("\n\nStarting server on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
