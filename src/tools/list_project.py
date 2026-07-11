from src.schema import Project
from typing import List
from src.client.openproject import OpenProjectClient

async def list_openproject_projects(client: OpenProjectClient) -> List[Project]:
    client = client.get_client()
    response = await client.get("/api/v3/projects")
    response.raise_for_status()
    data = response.json()
    return [Project(**item) for item in data["_embedded"]["elements"]]