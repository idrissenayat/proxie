import socketio
import structlog
from src.platform.config import settings
from src.platform.sessions import session_manager

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
async def connect(sid, environ):
    """Handle client connection."""
    # Auth logic can go here (check query params or headers)
    logger.info("socket_connected", sid=sid)
    
@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info("socket_disconnected", sid=sid)

@sio.event
async def join_session(sid, data):
    """Client joins a specific chat session room."""
    session_id = data.get("session_id")
    if session_id:
        await sio.enter_room(sid, f"session:{session_id}")
        logger.info("socket_joined_room", sid=sid, session_id=session_id)
        return {"status": "ok"}
    return {"status": "error", "message": "session_id required"}

@sio.event
async def chat_message(sid, data):
    """Handle incoming chat message via WebSocket."""
    # This will likely trigger the agent orchestrator in a future sprint
    session_id = data.get("session_id")
    content = data.get("content")
    
    logger.info("socket_chat_message", sid=sid, session_id=session_id)
    
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
