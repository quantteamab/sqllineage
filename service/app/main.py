"""Main FastAPI application for SQLLineage service."""

import json
import logging
import logging.handlers
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.routers import health, lineage


def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level.upper())

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(settings.log_level.upper())

    # Formatter
    if settings.log_format == "json":
        formatter = logging.Formatter(
            json.dumps(
                {
                    "timestamp": "%(asctime)s",
                    "level": "%(levelname)s",
                    "logger": "%(name)s",
                    "message": "%(message)s",
                }
            )
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {settings.log_level}, File: {settings.log_file}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    logger.info(f"Service port: {settings.service_port}")
    logger.info(f"Rate limit: {settings.rate_limit_rpm} requests/minute")
    logger.info(f"Request timeout: {settings.request_timeout_sec} seconds")
    logger.info(f"Max request size: {settings.max_request_size_mb} MB")
    logger.info(
        f"OpenMetadata configured: {settings.openmetadata_configured}"
    )

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.service_name}")


# Create FastAPI application
app = FastAPI(
    title="SQLLineage API",
    description="""
    SQL Lineage Analysis API - Analyze SQL queries to extract table and column lineage.

    ## Features
    - **Column Pairs**: Get column-level lineage as source-target pairs
    - **Table Lineage**: Extract source and target tables from SQL
    - **Verbose Column Lineage**: Get full column lineage paths
    - **Multiple Dialects**: Support for various SQL dialects (ANSI, Hive, SparkSQL, etc.)
    - **OpenMetadata Integration**: Optional metadata resolution from OpenMetadata
    - **Rate Limiting**: 100 requests per minute per IP
    - **Request Size Limit**: Up to 50MB SQL text per request

    ## Rate Limiting
    All API endpoints (except /health) are rate-limited to 100 requests per minute per IP address.
    Rate limit information is included in response headers:
    - `X-RateLimit-Limit`: Maximum requests allowed
    - `X-RateLimit-Remaining`: Requests remaining in current window
    - `X-RateLimit-Reset`: Unix timestamp when the window resets
    """,
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter middleware
app.add_middleware(RateLimiterMiddleware, requests_per_minute=settings.rate_limit_rpm)


# Request size validation middleware
@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    """Validate that request body doesn't exceed size limit."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length:
            content_length_bytes = int(content_length)
            if content_length_bytes > settings.max_request_size_bytes:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": f"Request body size ({content_length_bytes / 1024 / 1024:.2f}MB) "
                        f"exceeds maximum allowed size ({settings.max_request_size_mb}MB)"
                    },
                )

    return await call_next(request)


# Request timeout middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    # Log request
    logger = logging.getLogger(__name__)
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )

    return response


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger = logging.getLogger(__name__)
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger = logging.getLogger(__name__)
    logger.exception(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.log_level.upper() == "DEBUG" else None,
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(lineage.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
