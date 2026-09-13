import os
from dotenv import load_dotenv

load_dotenv()

class ProjectSettings:
    def __init__(self):
        self.project_name = "OpenProject MCP"
        self.version = "1.0.0"
        self.author = "akbted"
        self.description = "A project management tool for managing tasks and projects."

        self.LOG_FIRE_APIS = os.getenv("LOG_FIRE", "False").lower() == "true"

        self.LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
        self.LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")

        self.LITELLM_URL = os.getenv("LITELLM_URL", "")
        self.LITELLM_VIRTUAL_KEY = os.getenv("LITELLM_VIRTUAL_KEY", "")

        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB", "")

        self.REDIS_URL = os.getenv("REDIS_URL", "")
        self.QDRANT_URL = os.getenv("QDRANT_URL", "")




settings = ProjectSettings()

