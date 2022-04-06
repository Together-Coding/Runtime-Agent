import functools

import requests
from fastapi import APIRouter

from configs import settings
from server import sio
from server.websocket import InEvent, OutEvent

router = APIRouter(prefix='/ssh')


def ws_auth_required(func):
    @functools.wraps(func)
    async def decorated(sid, data):
        if not (await is_valid(sid)):
            sio.emit(OutEvent.ERROR,
                     {'type': 'auth', 'message': 'Not authorized'},
                     room=sid)
            return

        return await func(sid, data)

    return decorated


async def is_valid(sid):
    s = await sio.get_session(sid)
    return s['valid'] is True


@sio.event
async def connect(sid, environ, auth):
    print('Connect:', sid)
    await sio.emit(OutEvent.MESSAGE, 'connected')


@sio.event
async def disconnect(sid):
    print('Disconnect:', sid)


@sio.on(InEvent.AUTHENTICATE)
async def authenticate(sid, data):
    token = data.get('token')

    if not token:
        await sio.emit(OutEvent.ERROR,
                       {'type': 'missing field', 'message': '`token` is missing'},
                       room=sid)
        return

    try:
        resp = requests.post(settings.API_URL + '/auth/token', json={
            'token': token
        })
        resp.raise_for_status()

        """
        {
            'userId': 1,
            'email': '...', 
            'issuedAt': '2022-04-06T09:57:03.000+00:00', 
            'expiredAt': '2022-05-06T09:57:03.000+00:00', 
            'valid': True
        }
        """
        resp_data = resp.json()
    except requests.HTTPError:
        # When auth server is unhealthy, clear session data
        sio.save_session(sid, {})
        await sio.emit(OutEvent.ERROR,
                       {'type': 'common', 'message': 'Try again later'},
                       room=sid)
        return

    if resp_data.get('valid'):
        # Save information for later usage
        await sio.save_session(sid, resp_data)
        await sio.emit(OutEvent.AUTHENTICATE, 'Authenticated', room=sid)
    else:
        # Clear session data
        sio.save_session(sid, {})
        await sio.emit(OutEvent.ERROR,
                       {'type': 'auth', 'message': 'Invalid token'},
                       room=sid)

