#!/usr/bin/env python
"""
Example LiveKit token server for agents.

This server generates JWT tokens for participants to join LiveKit rooms.
It's essential for securing your LiveKit deployment by controlling who
can access rooms and what permissions they have.

Key features:
- CORS support for web frontends
- Configurable token expiry
- Room and participant name validation
- Proper error handling

Usage:
    python token_server.py

Environment variables:
    LIVEKIT_API_KEY: Your LiveKit API key
    LIVEKIT_API_SECRET: Your LiveKit API secret
    TOKEN_SERVER_PORT: Port to run on (default: 8080)
    CORS_ORIGINS: Comma-separated list of allowed origins
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from livekit import api

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("token-server")

# Configuration from environment
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
PORT = int(os.getenv("TOKEN_SERVER_PORT", "8080"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

# Validate required environment variables
if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")

# Create FastAPI app
app = FastAPI(
    title="LiveKit Token Server",
    description="Generate JWT tokens for LiveKit room access",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    """Request model for token generation."""
    room_name: str = Field(..., description="Name of the room to join")
    participant_name: str = Field(..., description="Name of the participant")
    metadata: Optional[str] = Field(None, description="Optional participant metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "room_name": "appointment-test-123",
                "participant_name": "user-456",
                "metadata": '{"role": "participant"}'
            }
        }


class TokenResponse(BaseModel):
    """Response model for token generation."""
    token: str = Field(..., description="JWT access token")
    url: str = Field(..., description="WebSocket URL for connection")
    expires_at: datetime = Field(..., description="Token expiration time")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "livekit-token-server",
        "timestamp": datetime.utcnow()
    }


@app.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Generate a LiveKit access token.
    
    This endpoint creates a JWT token that allows a participant to join
    a specific LiveKit room with the given permissions.
    
    Args:
        request: Token request with room and participant details
        
    Returns:
        TokenResponse with the JWT token and connection details
        
    Raises:
        HTTPException: If token generation fails
    """
    try:
        # Validate room name
        if not request.room_name or len(request.room_name) < 3:
            raise HTTPException(
                status_code=400,
                detail="Room name must be at least 3 characters long"
            )
        
        # Validate participant name
        if not request.participant_name or len(request.participant_name) < 3:
            raise HTTPException(
                status_code=400,
                detail="Participant name must be at least 3 characters long"
            )
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        
        # Configure token grants
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=request.room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ))
        
        # Add metadata if provided
        if request.metadata:
            token.with_metadata(request.metadata)
        
        # Set expiration
        token.with_ttl(timedelta(hours=TOKEN_EXPIRY_HOURS))
        
        # Generate the JWT token
        jwt_token = token.to_jwt()
        
        # Get WebSocket URL (from environment or default)
        ws_url = os.getenv("LIVEKIT_URL", "wss://your-project.livekit.cloud")
        
        logger.info(
            f"Token generated for user {request.participant_name} "
            f"in room {request.room_name}"
        )
        
        return TokenResponse(
            token=jwt_token,
            url=ws_url,
            expires_at=expires_at
        )
        
    except Exception as e:
        logger.error(f"Failed to generate token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate token: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "LiveKit Token Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /token": "Generate access token",
            "GET /health": "Health check",
        },
        "documentation": "/docs",
    }


if __name__ == "__main__":
    logger.info(f"Token server starting on port {PORT}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    logger.info(f"Token expiry: {TOKEN_EXPIRY_HOURS} hours")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )