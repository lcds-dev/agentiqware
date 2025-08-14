"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque

# In-memory rate limiting store (use Redis in production)
rate_limit_store: Dict[str, Deque[float]] = defaultdict(deque)

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Get client IP
    client_ip = request.client.host
    
    # Rate limit configuration
    max_requests = 100
    time_window = 60  # 60 seconds
    
    current_time = time.time()
    
    # Clean old requests outside time window
    client_requests = rate_limit_store[client_ip]
    while client_requests and client_requests[0] <= current_time - time_window:
        client_requests.popleft()
    
    # Check if rate limit exceeded
    if len(client_requests) >= max_requests:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "status": "error",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": int(time_window)
            },
            headers={"Retry-After": str(time_window)}
        )
    
    # Add current request
    client_requests.append(current_time)
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = max_requests - len(client_requests)
    reset_time = int(current_time + time_window)
    
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    return response