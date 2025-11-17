"""Rate limiting middleware for API requests."""

import time
from collections import defaultdict, deque
from typing import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Tracks requests per IP address and enforces a requests-per-minute limit.
    """

    def __init__(self, app, requests_per_minute: int = 100):
        """
        Initialize rate limiter.

        :param app: FastAPI application
        :param requests_per_minute: Maximum requests allowed per minute
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        # Store timestamps of requests per IP
        self.request_timestamps: defaultdict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting.

        :param request: Incoming request
        :param call_next: Next middleware/handler
        :return: Response
        """
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old timestamps outside the window
        self._clean_old_timestamps(client_ip, current_time)

        # Check if limit exceeded
        if len(self.request_timestamps[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_minute,
                    "window": "1 minute",
                    "message": f"Too many requests. Maximum {self.requests_per_minute} requests per minute allowed.",
                },
            )

        # Add current request timestamp
        self.request_timestamps[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_timestamps[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_size)
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Checks X-Forwarded-For header first (for proxy/load balancer scenarios).

        :param request: Incoming request
        :return: Client IP address
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_old_timestamps(self, client_ip: str, current_time: float) -> None:
        """
        Remove timestamps outside the sliding window.

        :param client_ip: Client IP address
        :param current_time: Current timestamp
        """
        cutoff_time = current_time - self.window_size
        timestamps = self.request_timestamps[client_ip]

        # Remove old timestamps from the left side of deque
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.popleft()

        # Clean up empty entries to prevent memory leak
        if not timestamps:
            del self.request_timestamps[client_ip]
