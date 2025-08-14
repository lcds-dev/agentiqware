"""
Logging middleware
"""

import time
import logging
from fastapi import Request
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """Request/Response logging middleware"""
    
    start_time = time.time()
    
    # Log request
    request_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "request_id": getattr(request.state, "request_id", None)
    }
    
    logger.info(f"Request started: {json.dumps(request_data)}")
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        response_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "request_id": getattr(request.state, "request_id", None)
        }
        
        logger.info(f"Request completed: {json.dumps(response_data)}")
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "process_time": round(process_time, 4),
            "request_id": getattr(request.state, "request_id", None)
        }
        
        logger.error(f"Request failed: {json.dumps(error_data)}")
        raise