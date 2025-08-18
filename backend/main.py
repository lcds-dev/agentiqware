"""
Agentiqware Backend - Main Application
"""

import os
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import auth, flows, billing, admin, webhooks, components

# Import middleware
from middleware.authentication import verify_token
from middleware.rate_limiting import rate_limit_middleware
from middleware.logging import logging_middleware

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Agentiqware Backend...")
    # Initialize services
    yield
    # Shutdown
    print("Shutting down Agentiqware Backend...")

# Create FastAPI app
app = FastAPI(
    title="Agentiqware API",
    description="RPA & Digital Agents Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://agentiqware.com").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Security middleware
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,agentiqware.com,*.agentiqware.com").split(",")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[host.strip() for host in allowed_hosts]
)

# Custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(flows.router, prefix="/api/v1/flows", tags=["Flows"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(components.router, prefix="/api", tags=["Components"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agentiqware-backend"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Agentiqware API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "False") == "True"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )
