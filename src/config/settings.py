import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class PROJECTSETTINGS(BaseSettings):

    model_config = SettingsConfigDict(
            env_file=ENV_FILE,
            env_file_encoding="utf-8",
            extra="ignore"
        )
    app_name: str = "OpenProject MCP"
    OPENPROJECT_TOKEN: str
    OPENPROJECT_APIROOT: str

_instance = None

def get_settings():
    global _instance
    if _instance is None:
        _instance = PROJECTSETTINGS()
    return _instance

setting = get_settings()

if __name__ == "__main__":
    
    print(setting.OPENPROJECT_TOKEN)
    print(setting.OPENPROJECT_APIROOT)