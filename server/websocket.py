import socketio
from fastapi import FastAPI


def create_websocket(app: FastAPI):
    sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
    return sio, socketio.ASGIApp(sio, app)


class InEvent:
    SSH_CONNECT = 'SSH_CONNECT'  # SSH connection request
    SSH = 'SSH'  # Communicate with SSH terminal
    AUTHENTICATE = 'AUTHENTICATE'


class OutEvent:
    MESSAGE = 'MESSAGE'
    ERROR = 'ERROR'
    SSH_REFLECT = 'SSH_REFLECT'
    AUTHENTICATE = 'AUTHENTICATE'
