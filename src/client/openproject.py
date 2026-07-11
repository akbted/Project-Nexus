import httpx
from typing import List
from src.config.settings import PROJECTSETTINGS
from src.client.base import BaseOpenProjectClient
from src.schema import Project

class OpenProjectClient(BaseOpenProjectClient):
    def __init__(self, settings: PROJECTSETTINGS):
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.OPENPROJECT_APIROOT,
            auth=httpx.BasicAuth("apikey", settings.OPENPROJECT_TOKEN),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10.0,
        )

    def get_client(self):
        return self.client

    async def close(self):
        await self.client.aclose()

if __name__ == "__main__":
    pass

        