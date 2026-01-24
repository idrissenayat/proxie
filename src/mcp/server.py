from mcp.server import Server
from mcp.types import Tool, TextContent, EmbeddedResource
from mcp.shared.exceptions import McpError
from typing import Any, Sequence

from src.mcp import handlers

# Initialize MCP Server
mcp_server = Server("proxie")

@mcp_server.list_tools()
async def handle_list_tools() -> Sequence[Tool]:
    """List available tools."""
    return [
        Tool(
            name="create_service_request",
            description="Create a new service request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "consumer_id": {"type": "string"},
                    "service_category": {"type": "string"},
                    "service_type": {"type": "string"},
                    "raw_input": {"type": "string"},
                    "requirements": {"type": "object"},
                    "location": {"type": "object"},
                    "timing": {"type": "object"},
                    "budget": {"type": "object"}
                },
                "required": ["consumer_id", "service_category", "service_type"]
            }
        ),
        Tool(
            name="get_offers",
            description="Get offers for a service request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string"}
                },
                "required": ["request_id"]
            }
        ),
        Tool(
            name="accept_offer",
            description="Accept an offer and create a booking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "offer_id": {"type": "string"},
                    "selected_slot": {"type": "object"}
                },
                "required": ["offer_id", "selected_slot"]
            }
        ),
        Tool(
            name="submit_review",
            description="Submit a review for a completed booking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string"},
                    "rating": {"type": "integer"},
                    "comment": {"type": "string"}
                },
                "required": ["booking_id", "rating"]
            }
        ),
        Tool(
            name="get_matching_requests",
            description="Get service requests matching provider's profile.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider_id": {"type": "string"}
                },
                "required": ["provider_id"]
            }
        ),
        Tool(
            name="submit_offer",
            description="Submit an offer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string"},
                    "provider_id": {"type": "string"},
                    "price": {"type": "number"},
                    "available_slots": {"type": "array"},
                    "message": {"type": "string"}
                },
                "required": ["request_id", "provider_id", "price", "available_slots"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: Any) -> Sequence[TextContent | EmbeddedResource]:
    """Handle tool execution."""
    try:
        from uuid import UUID
        
        args = arguments or {}
        
        if name == "create_service_request":
            result = handlers.create_service_request(
                UUID(args["consumer_id"]),
                args["service_category"],
                args["service_type"],
                args.get("raw_input", ""),
                args.get("requirements", {}),
                args.get("location", {}),
                args.get("timing", {}),
                args.get("budget", {})
            )
            return [TextContent(type="text", text=str(result))]
            
        elif name == "get_offers":
            result = handlers.get_offers(UUID(args["request_id"]))
            return [TextContent(type="text", text=str(result))]
            
        elif name == "accept_offer":
            result = handlers.accept_offer(UUID(args["offer_id"]), args["selected_slot"])
            return [TextContent(type="text", text=str(result))]
            
        elif name == "submit_review":
            result = handlers.submit_review(
                UUID(args["booking_id"]), 
                args["rating"], 
                args.get("comment", "")
            )
            return [TextContent(type="text", text=str(result))]
            
        elif name == "get_matching_requests":
            result = handlers.get_matching_requests(UUID(args["provider_id"]))
            return [TextContent(type="text", text=str(result))]
            
        elif name == "submit_offer":
            result = handlers.submit_offer(
                UUID(args["request_id"]),
                UUID(args["provider_id"]),
                args["price"],
                args["available_slots"],
                args.get("message", "")
            )
            return [TextContent(type="text", text=str(result))]
            
        else:
            raise McpError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
