from fastapi import APIRouter, Depends, status, Request, HTTPException, Response
from sse_starlette.sse import EventSourceResponse
from mcp.server.sse import SseServerTransport
from typing import Optional

from src.platform.config import settings
from src.mcp.server import mcp_server

router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    responses={404: {"description": "Not found"}},
)

# Auth dependency
async def verify_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
         raise HTTPException(status_code=401, detail="Missing Authentication")
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
         raise HTTPException(status_code=401, detail="Invalid Authentication type")
         
    token = parts[1]
    if token != settings.MCP_API_KEY:
         raise HTTPException(status_code=403, detail="Invalid API Key")
    return token

# Global dictionary to hold transports for active sessions
# Key: Session ID (or verify if transport manages it)
# The SseServerTransport doesn't handle session persistence across requests by default automatically for the POST endpoint?
# The POST /messages endpoint needs to find the correct transport to push data to.
# SseServerTransport design in mcp-python sdk is:
# 1. GET /sse creates transport, starts session.
# 2. POST /messages?session_id=... maps to that transport.
# We need to store them.

_transports = {}

@router.get("/sse")
async def handle_sse(request: Request, api_key: str = Depends(verify_api_key)):
    """
    Establish MCP SSE connection.
    """
    transport = SseServerTransport("/mcp/messages")
    
    async def event_generator():
        # Start the transport and server connection
        # This will yield SSE events
        async with mcp_server.connect(transport) as connection:
             # Store transport for POST handling
             # We assume transport.session_id is generated after start?
             # Actually, SseServerTransport might not expose a session_id until we read it or it might generate one.
             # We need to capture the session ID. 
             # Let's peek at python-sdk sse implementation:
             # usually works by yielding invalid SSE comment with session ID first.
             
             # We can't easily map the POST request back to this specific transport instance 
             # unless we store it.
             # SseServerTransport presumably has an ID.
             pass
             
             # We yield from the transport's outgoing messages
             async for message in transport.incoming_messages():
                 # This is client -> server? No. 
                 # server.connect() runs the loop.
                 # SseServerTransport.handle_post_message pushes to the server.
                 # Incoming to the client is via yield.
                 pass
                 
    # Re-evaluating: The mcp library's SseServerTransport is a bit complex to host manually in FastAPI 
    # without using the Starlette adapter provided by the library if it exists.
    # But let's try the Starlette way manually.
    
    # Create transport
    transport = SseServerTransport("/mcp/messages")
    
    async def sse_generator():
        await transport.start()
        # Store transport so POST requests can find it
        # Note: Session ID is usually determined by the library. 
        # For this MVP, we might hack it: SseServerTransport uses memory?
        # Actually, without a shared state store, this is hard if creating new transport per request.
        # BUT, the GET request stays open. The POST request comes in parallel.
        # We need a shared registry `_transports`.
        
        # Assume transport has `id`.
        # session_id = str(id(transport)) # Too risky
        # Let's allow the transport to generate the endpoint?
        
        # Using a simpler pattern found in mcp examples:
        async with mcp_server.connect(transport):
            # We need to expose this transport to the POST endpoint
            _transports[transport.session_id] = transport
            
            try:
                # Yield events from transport
                async for message in transport.sse_messages():
                    yield message
            finally:
                if transport.session_id in _transports:
                    del _transports[transport.session_id]

    return EventSourceResponse(sse_generator())

@router.post("/messages")
async def handle_messages(request: Request):
    """
    Handle incoming MCP messages (JSON-RPC) via POST.
    """
    # Verify Auth (Query param or Header? Spec says Header for connection)
    # Ideally auth here too.
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header.split()[1] != settings.MCP_API_KEY:
         raise HTTPException(status_code=403, detail="Invalid API Key")

    session_id = request.query_params.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")
        
    transport = _transports.get(session_id)
    if not transport:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Read body
    try:
        message = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    # Delegate to transport
    await transport.handle_post_message(message)
    
    return Response(status_code=202)
