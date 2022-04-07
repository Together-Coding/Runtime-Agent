import os

from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    DEBUG: bool = False


global_settings = GlobalSettings()


class Settings(BaseSettings):
    AGENT_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/agent'
    USERNAME: str = 'together'
    DEFAULT_WORKING_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/app'

    API_URL = 'http://api.together-coding.com'  # FIXME use HTTPS
    CORS_ALLOW_ORIGIN = '*' if global_settings.DEBUG else ''  # FIXME IDE domain


settings = Settings()
