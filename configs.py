import os
from typing import Union
from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    DEBUG: bool = False
    BRIDGE_KEY_NAME: str = 'bridge_key'
    BRIDGE_KEY = ''  # Used to authenticate itself to bridge server
    SERVER_INIT: bool = False  # Whether it is initialized by communicating with bridge server.
    # TODO: Make `global_settings` be synced across uvicorn processes


global_settings = GlobalSettings()


class Settings(BaseSettings):
    # Machine and SSH related
    AGENT_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/agent'
    USER_DIRECTORY: str = os.getcwd() if global_settings.DEBUG else '/usr/src/app'
    USERNAME: str = 'together'
    FIXMED_PASSWORD: Union[str, bool] = 'ttest' if global_settings.DEBUG else False
    SSH_PORT = 22

    # API related
    API_URL = 'http://api.together-coding.com'  # FIXME use HTTPS
    BRIDGE_URL = 'http://127.0.0.1:8080' if global_settings.DEBUG else 'https://bridge.together-coding.com'


settings = Settings()


def read_bridge_key():
    """ Read key into settings """
    if os.path.exists(global_settings.BRIDGE_KEY_NAME):
        with open(global_settings.BRIDGE_KEY_NAME, 'rt') as fp:
            global_settings.BRIDGE_KEY = fp.read()
    else:
        global_settings.BRIDGE_KEY = ''
