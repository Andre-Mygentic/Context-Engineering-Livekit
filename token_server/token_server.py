"""
FastAPI Token Server for LiveKit Authentication

This server generates JWT tokens for LiveKit room access.
It handles CORS for frontend applications and provides
secure token generation with proper claims and permissions.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("token-server")

# LiveKit configuration from environment
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in environment")

# Server configuration
PORT = int(os.getenv("TOKEN_SERVER_PORT", "8001"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info(f"Token server starting on port {PORT}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    logger.info(f"Token expiry: {TOKEN_EXPIRY_HOURS} hours")
    yield
    # Shutdown
    logger.info("Token server shutting down")


# Create FastAPI app
app = FastAPI(
    title="LiveKit Token Server",
    description="Generate JWT tokens for LiveKit room access",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Request/Response models
class TokenRequest(BaseModel):
    """Request model for token generation."""
    user_email: str = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    user_id: str = Field(..., description="Unique user identifier")
    room_name: Optional[str] = Field(None, description="Specific room to join")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "sarah@example.com",
                "full_name": "Sarah Johnson",
                "user_id": "user-123",
                "room_name": "appointment-456"
            }
        }


class TokenResponse(BaseModel):
    """Response model for token generation."""
    token: str = Field(..., description="JWT token for LiveKit")
    room_name: str = Field(..., description="Room name to join")
    

def generate_room_name(user_email: str) -> str:
    """Generate a unique room name based on user email and timestamp."""
    # Simple room name generation - you might want something more sophisticated
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email_prefix = user_email.split("@")[0]
    return f"{email_prefix}-{timestamp}"


def create_token(
    identity: str,
    name: str,
    room: str,
    metadata: dict = None,
    can_publish: bool = True,
    can_subscribe: bool = True,
    can_update_metadata: bool = True,
) -> str:
    """
    Create a LiveKit JWT token with appropriate claims.
    
    Args:
        identity: Unique user identifier
        name: Display name
        room: Room name to join
        metadata: Additional metadata to include
        can_publish: Permission to publish media
        can_subscribe: Permission to subscribe to media
        can_update_metadata: Permission to update own metadata
        
    Returns:
        JWT token string
    """
    # Token expiry
    now = datetime.utcnow()
    exp = now + timedelta(hours=TOKEN_EXPIRY_HOURS)
    
    # Build video grants
    video_grants = {
        "room": room,
        "roomJoin": True,
        "canPublish": can_publish,
        "canSubscribe": can_subscribe,
        "canUpdateOwnMetadata": can_update_metadata,
    }
    
    # Build JWT claims
    claims = {
        "iss": LIVEKIT_API_KEY,  # Issuer is the API key
        "sub": identity,  # Subject is the user identity
        "iat": int(now.timestamp()),  # Issued at
        "nbf": int(now.timestamp()),  # Not before
        "exp": int(exp.timestamp()),  # Expiry
        "name": name,  # Display name
        "video": video_grants,  # LiveKit specific grants
    }
    
    # Add metadata if provided
    if metadata:
        claims["metadata"] = str(metadata)  # LiveKit expects string metadata
    
    # Sign and return the token
    token = jwt.encode(claims, LIVEKIT_API_SECRET, algorithm="HS256")
    return token


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LiveKit Token Server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Generate a LiveKit JWT token for a user.
    
    This endpoint creates a secure token that allows a user to join
    a LiveKit room with appropriate permissions.
    """
    try:
        # Use provided room name or generate one
        room_name = request.room_name or generate_room_name(request.user_email)
        
        # Create metadata
        metadata = {
            "user_email": request.user_email,
            "user_id": request.user_id,
            "full_name": request.full_name,
        }
        
        # Generate token
        token = create_token(
            identity=request.user_id,
            name=request.full_name,
            room=room_name,
            metadata=metadata,
            can_publish=True,  # Allow audio/video publishing
            can_subscribe=True,  # Allow receiving audio/video
            can_update_metadata=True,  # Allow updating own metadata
        )
        
        logger.info(f"Token generated for user {request.user_id} in room {room_name}")
        
        return TokenResponse(token=token, room_name=room_name)
        
    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate token")


@app.post("/validate")
async def validate_token(token: str):
    """
    Validate a LiveKit JWT token.
    
    This endpoint can be used to verify token validity and extract claims.
    """
    try:
        # Decode and validate the token
        claims = jwt.decode(
            token,
            LIVEKIT_API_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        
        return {
            "valid": True,
            "identity": claims.get("sub"),
            "name": claims.get("name"),
            "room": claims.get("video", {}).get("room"),
            "expires_at": datetime.fromtimestamp(claims.get("exp", 0)).isoformat()
        }
        
    except JWTError as e:
        return {
            "valid": False,
            "error": str(e)
        }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "token_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )