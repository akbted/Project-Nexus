from src.client.base import BaseOpenProjectClient
from src.client.openproject import OpenProjectClient
from src.config.settings import PROJECTSETTINGS

class ClientCreator():
    @staticmethod # Why static method ?
    def create(settings: PROJECTSETTINGS) -> BaseOpenProjectClient:
        return OpenProjectClient(settings)
    
    
