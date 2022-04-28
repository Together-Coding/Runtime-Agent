import os

from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    DEBUG: bool = False
    BRIDGE_KEY_NAME: str = 'bridge_key'
    BRIDGE_KEY = ''  # Used to authenticate itself to bridge server
    SERVER_INIT: bool = False  # Whether it is initialized by communicating with bridge server.
    # TODO: Is `global_settings` unique under uvicorn?


global_settings = GlobalSettings()


class Settings(BaseSettings):
    AGENT_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/agent'
    USERNAME: str = 'together'
    DEFAULT_WORKING_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/app'

    CORS_ALLOW_ORIGIN = '*' if global_settings.DEBUG else '*'  # FIXME: IDE domain
    API_URL = 'http://api.together-coding.com'  # FIXME use HTTPS
    BRIDGE_URL = 'https://dev-bridge.together-coding.com' if global_settings.DEBUG else 'https://bridge.together-coding.com'


settings = Settings()


def read_bridge_key():
    """ Read key into settings """
    if os.path.exists(global_settings.BRIDGE_KEY_NAME):
        with open(global_settings.BRIDGE_KEY_NAME, 'rt') as fp:
            global_settings.BRIDGE_KEY = fp.read()
    else:
        global_settings.BRIDGE_KEY = ''
