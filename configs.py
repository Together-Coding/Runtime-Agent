import os


DEBUG = True

AGENT_DIRECTORY = os.getcwd() if DEBUG else '/usr/src/agent'
USERNAME = 'together'
DEFAULT_WORKING_DIRECTORY = os.getcwd() if DEBUG else '/usr/src/app'
