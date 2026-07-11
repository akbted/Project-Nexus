from src.schema import Project
from typing import List
from src.client.openproject import OpenProjectClient


async def list_project_workpackages(client: OpenProjectClient, project_id):
    client = client.get_client()
    response = await client.get(f"/api/v3/projects/{project_id}/work_packages")
    response.raise_for_status()
    data = response.json()
    return data