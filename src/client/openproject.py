import httpx
import asyncio
from src.config.settings import PROJECTSETTINGS
from src.client.base import BaseOpenProjectClient

class OpenProjectClient(BaseOpenProjectClient):
    def __init__(self, settings: PROJECTSETTINGS):
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.uri,
            auth=httpx.BasicAuth("apikey", settings.token),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10.0,
        )

    async def close(self):
        await self.client.aclose()

    async def list_projects(self):
        response = await self.client.get("/api/v3/projects")
        response.raise_for_status()
        data = response.json()
        return data
    
    async def get_projects(self, project_id):
        pass

    async def list_work_packages(self, project_id):
        pass

    async def get_work_package(self, work_package_id):
        pass

    async def create_work_package(self, project_id):
        pass


if __name__ == "__main__":
    pass

        