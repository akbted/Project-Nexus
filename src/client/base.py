from abc import ABC, abstractmethod

class BaseOpenProjectClient(ABC):
    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    async def close(self):
        pass