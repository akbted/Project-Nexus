from typing import List
from src.schema import WorkPackage
from src.client.openproject import OpenProjectClient


async def list_project_workpackages(client: OpenProjectClient, project_id) -> List[WorkPackage]:
    http = client.get_client()
    response = await http.get(f"/api/v3/projects/{project_id}/work_packages")
    response.raise_for_status()
    data = response.json()
    return [WorkPackage(**item) for item in data["_embedded"]["elements"]]