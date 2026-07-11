from abc import ABC, abstractmethod

class BaseOpenProjectClient(ABC):

    @abstractmethod
    def get_client(self):
        return self.client

    @abstractmethod
    async def close(self):
        await self.client.aclose()