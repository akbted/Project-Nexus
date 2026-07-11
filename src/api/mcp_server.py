from fastmcp import FastMCP
from src.api.middleware import AuthMiddleware
from contextlib import asynccontextmanager
from src.factories import ClientCreator
from src.config import get_settings
from src.tools import list_openproject_projects, list_project_workpackages

@asynccontextmanager
async def lifespan(server: FastMCP):
    settings = get_settings()
    client = ClientCreator.create(settings)

    yield {
        "client" : client
    }

    await client.close()

mcp = FastMCP("OpenProject", lifespan=lifespan)

# Add auth middleware
mcp.add_middleware(AuthMiddleware(valid_api_keys=["my-secret-key-123"]))


@mcp.tool()
async def list_projects(ctx):
    """List all the projects in OpenProject"""
    try:
        client = ctx.request_context.lifespan_context["client"]
        return await list_openproject_projects(client)
    except Exception as e:
        return f"Failed to run List Projects Tool {e}"


@mcp.tool()
async def list_workpackages(ctx, project_id):
    """List work packages for a project"""
    if not project_id:
        return "Missing Project_ID"
    try:
        client = ctx.request_context.lifespan_context["client"]
        return await list_project_workpackages(client, project_id)
    except Exception as e:
        return f"Failed to run List Work Packages Tool {e}"



if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http")

