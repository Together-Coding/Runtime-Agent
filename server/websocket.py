import socketio
from fastapi import FastAPI


def create_websocket(app: FastAPI):
    sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
    return sio, socketio.ASGIApp(sio, app)


class InEvent:
    SSH_CONNECT = 'SSH_CONNECT'  # SSH connection request
    SSH = 'SSH'  # Communicate with SSH terminal
    SSH_RESIZE = 'SSH_RESIZE'  # Resize pty
    AUTHENTICATE = 'AUTHENTICATE'


class OutEvent:
    MESSAGE = 'MESSAGE'
    ERROR = 'ERROR'
    AUTHENTICATE = 'AUTHENTICATE'
    SSH_RELAY = 'SSH_RELAY'
    SSH_DOWN = 'SSH_DOWN'


class ErrorType:
    AUTH = 'auth'
    UNKNOWN = 'unknown'
    MISSING_FIELD = 'missing field'
    COMMON = 'common'
    SSH = 'ssh'
