from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError


class AuthMiddleware(Middleware):
    """Middleware that checks for a valid API key before tool execution."""

    def __init__(self, valid_api_keys: list[str]):
        self.valid_api_keys = valid_api_keys

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Get the API key from the request context
        api_key = context.fastmcp_context.get_state("api_key")

        if not api_key:
            raise ToolError("Access denied: No API key provided")

        if api_key not in self.valid_api_keys:
            raise ToolError("Access denied: Invalid API key")

        # Store user info in context for tools to use
        context.fastmcp_context.set_state("authenticated", True)

        return await call_next(context)