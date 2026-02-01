import socketio
import structlog
from typing import Optional, Dict, Any
from src.platform.config import settings
from src.platform.sessions import session_manager
from src.platform.auth import verify_token

logger = structlog.get_logger()

# Create Socket.io server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.cors_origins_list
)

# Wrapper for FastAPI integration
# Note: We specify the socketio_path to match what the client expects
socket_app = socketio.ASGIApp(sio, socketio_path='socket.io')

def create_socket_app(main_app):
    """Wrap a FastAPI app with Socket.io ASGI middleware."""
    return socketio.ASGIApp(sio, other_asgi_app=main_app, socketio_path='/ws/socket.io')

@sio.event
async def connect(sid, environ, auth: Optional[Dict[str, Any]] = None):
    """
    Handle client connection with JWT authentication.
    
    Accepts token via:
    1. auth['token'] - Preferred method (Socket.io auth object)
    2. Query parameter 'token' - Fallback for clients that can't use auth object
    
    Returns False to reject the connection if authentication fails.
    """
    token = None
    
    # Try to get token from auth object first (preferred)
    if auth and isinstance(auth, dict):
        token = auth.get("token")
    
    # Fallback: Check query parameters
    if not token and environ.get("QUERY_STRING"):
        query_params = environ["QUERY_STRING"].split("&")
        for param in query_params:
            if param.startswith("token="):
                token = param.split("=", 1)[1]
                break
    
    # Fallback: Check Authorization header
    if not token:
        auth_header = environ.get("HTTP_AUTHORIZATION") or environ.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    
    # Allow connections in development/testing without auth (for testing)
    if settings.ENVIRONMENT in ["testing", "development"]:
        bypass_secret = getattr(settings, "LOAD_TEST_SECRET", None)
        if bypass_secret and environ.get("HTTP_X_LOAD_TEST_SECRET") == bypass_secret:
            logger.info("socket_auth_bypass", sid=sid, type="load_test")
            # Store test user info in session
            await sio.save_session(sid, {
                "user_id": environ.get("HTTP_X_TEST_USER_ID", "test_user"),
                "role": environ.get("HTTP_X_TEST_USER_ROLE", "consumer"),
                "authenticated": True
            })
            logger.info("socket_connected", sid=sid, user_id="test_user")
            return True
    
    # Require authentication
    if not token:
        logger.warning("socket_connection_rejected", sid=sid, reason="no_token")
        return False  # Reject connection
    
    try:
        # Verify JWT token
        decoded_token = verify_token(token)
        user_id = decoded_token.get("sub")
        
        if not user_id:
            logger.warning("socket_connection_rejected", sid=sid, reason="invalid_token_no_user_id")
            return False
        
        # Store user info in Socket.io session
        await sio.save_session(sid, {
            "user_id": user_id,
            "email": decoded_token.get("email"),
            "role": decoded_token.get("public_metadata", {}).get("role"),
            "authenticated": True,
            "token_data": decoded_token
        })
        
        logger.info("socket_connected", sid=sid, user_id=user_id)
        return True  # Accept connection
        
    except Exception as e:
        logger.error("socket_auth_failed", sid=sid, error=str(e))
        return False  # Reject connection
    
@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    # Get session info before clearing
    session = await sio.get_session(sid)
    user_id = session.get("user_id") if session else None
    logger.info("socket_disconnected", sid=sid, user_id=user_id)

@sio.event
async def join_session(sid, data):
    """Client joins a specific chat session room."""
    # Verify user is authenticated
    session = await sio.get_session(sid)
    if not session or not session.get("authenticated"):
        logger.warning("socket_unauthorized_action", sid=sid, action="join_session")
        return {"status": "error", "message": "Authentication required"}
    
    session_id = data.get("session_id")
    if session_id:
        await sio.enter_room(sid, f"session:{session_id}")
        logger.info("socket_joined_room", sid=sid, session_id=session_id, user_id=session.get("user_id"))
        return {"status": "ok"}
    return {"status": "error", "message": "session_id required"}

@sio.event
async def chat_message(sid, data):
    """Handle incoming chat message via WebSocket."""
    # Verify user is authenticated
    session = await sio.get_session(sid)
    if not session or not session.get("authenticated"):
        logger.warning("socket_unauthorized_action", sid=sid, action="chat_message")
        await sio.emit("error", {"message": "Authentication required"}, room=sid)
        return
    
    session_id = data.get("session_id")
    content = data.get("content")
    user_id = session.get("user_id")
    
    logger.info("socket_chat_message", sid=sid, session_id=session_id, user_id=user_id)
    
    # Broadcast echo (for testing) or send to agent logic
    await sio.emit("chat:echo", data, room=f"session:{session_id}")

async def broadcast_agent_response(session_id: str, content: str, data: dict = None):
    """Utility to send agent response to all clients in a session room."""
    await sio.emit("chat:response", {
        "session_id": session_id,
        "content": content,
        "data": data
    }, room=f"session:{session_id}")

async def emit_notification(user_id: str, event: str, payload: dict):
    """Utility to send notification to a specific user (future logic)."""
    await sio.emit(event, payload, room=f"user:{user_id}")
