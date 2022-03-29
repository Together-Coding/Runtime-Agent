import os

from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    DEBUG: bool = True


global_settings = GlobalSettings()


class Settings(BaseSettings):
    AGENT_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/agent'
    USERNAME: str = 'together'
    DEFAULT_WORKING_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/app'


settings = Settings()
