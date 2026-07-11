from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request
from fastmcp.exceptions import ToolError


class AuthMiddleware(Middleware):
    """Middleware that checks for a valid API key before tool execution."""

    def __init__(self, valid_api_keys: list[str]):
        self.valid_api_keys = valid_api_keys

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Get the API key from the request context
        try:
            request = get_http_request()
            api_key = request.headers.get("x-api-key")
        except RuntimeError:
            # stdio mode — skip auth
            return await call_next(context)


        if not api_key:
            raise ToolError("Access denied: No API key provided")

        if api_key not in self.valid_api_keys:
            raise ToolError("Access denied: Invalid API key")

        # Store user info in context for tools to use
        context.fastmcp_context.set_state("authenticated", True)

        return await call_next(context)