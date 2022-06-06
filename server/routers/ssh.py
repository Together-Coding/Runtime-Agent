import functools

import requests
from fastapi import APIRouter

from configs import settings, global_settings
from server import sio
from server.utils import ws_session
from server.websocket import InEvent, OutEvent, ErrorType
from server.models import User
from server.utils.ssh import ssh_connect, SSHWorker, Reason
from server.utils.exceptions import SSHConnectionException

router = APIRouter(prefix='/ssh')


def server_init_required(func):
    """
    This server must be initialized first to process the decorated function.
    Initialization is done by main.init_server at its startup.
    """
    @functools.wraps(func)
    async def decorated(sid, data):
        if not global_settings.SERVER_INIT or not global_settings.BRIDGE_KEY:
            await sio.emit(OutEvent.ERROR,
                           {'type': ErrorType.INIT_NEEDED,
                            'message': 'Server is not initialized.'},
                           room=sid)
        else:
            await func(sid, data)

    return decorated


def ws_auth_required(func):
    @functools.wraps(func)
    async def decorated(sid, data):
        if not (await is_valid(sid)):
            await sio.emit(OutEvent.ERROR,
                           {'type': ErrorType.AUTH, 'message': 'Not authorized'},
                           room=sid)
        else:
            await func(sid, data)

    return decorated


async def is_valid(sid):
    valid = await ws_session.get(sid, 'valid')
    return valid is True


@sio.event
async def connect(sid, environ, auth):
    await ws_session.update(sid, {'ip': environ['REMOTE_ADDR']})
    await sio.emit(OutEvent.MESSAGE, 'connected')


@sio.event
async def disconnect(sid):
    """ Cleanup ssh worker """
    ssh_worker: SSHWorker = await ws_session.get(sid, 'ssh')
    if ssh_worker:
        reason = Reason.WS_DISCONNECTED
        ssh_worker.stop_tasks(reason)
        await ssh_worker.cleanup(reason, False)


@sio.on(InEvent.AUTHENTICATE)
async def authenticate(sid, data):
    token = data.get('token')

    if not token:
        await sio.emit(OutEvent.ERROR,
                       {'type': ErrorType.MISSING_FIELD, 'message': '`token` is missing'},
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
        await sio.emit(OutEvent.ERROR,
                       {'type': ErrorType.COMMON, 'message': 'Try again later'},
                       room=sid)
        return

    if resp_data.get('valid'):
        # Save information for later usage
        await ws_session.update(sid, resp_data)
        await sio.emit(OutEvent.AUTHENTICATE, OutEvent.AUTHENTICATE, room=sid)
    else:
        # Clear session data except IP
        await ws_session.clear(sid, ['ip'])
        await sio.emit(OutEvent.ERROR,
                       {'type': ErrorType.AUTH, 'message': 'Invalid token'},
                       room=sid)


@sio.on(InEvent.SSH_CONNECT)
@ws_auth_required
@server_init_required
async def connect_to_ssh(sid, data=None):
    s = await sio.get_session(sid)
    user = User(user_id=s['userId'], ip=s['ip'])

    headers = {'X-API-KEY': global_settings.BRIDGE_KEY}
    resp = requests.get(settings.BRIDGE_URL + f'/api/containers/info',
                        headers=headers)

    if not resp.ok:
        # TODO: send sentry
        try:
            reason = resp.json()['error']
        except:
            reason = f'Bridge is dead. ({resp.status_code})'
        await sio.emit(OutEvent.ERROR,
                       {'type': ErrorType.UNKNOWN, 'message': reason},
                       room=sid)
        return

    resp = resp.json()
    ssh_data = {
        'cont_ip': '127.0.0.1',  # Fixed value
        'cont_user': resp['cont_user'],
        'cont_auth_type': resp['cont_auth_type'],
        'cont_auth': resp['cont_auth'],
        'cont_port': settings.SSH_PORT,  # Fixed value for now
    }

    try:
        ssh_worker = ssh_connect(sio,
                                 user,
                                 ssh_data['cont_ip'],
                                 ssh_data['cont_user'],
                                 ssh_data['cont_auth_type'],
                                 ssh_data['cont_auth'],
                                 ssh_data['cont_port'])
        ssh_worker.sio_accepted(sid)
        await ws_session.update(sid, {'ssh': ssh_worker})
        return await ssh_worker.run()
    except SSHConnectionException as e:
        message = str(e)
    except:
        message = Reason.SSH_FAIL

    await sio.emit(OutEvent.ERROR,
                   {'type': ErrorType.SSH, 'message': message},
                   room=sid)


@sio.on(InEvent.SSH)
@ws_auth_required
async def recv_from_client(sid, data):
    ssh_worker: SSHWorker = await ws_session.get(sid, 'ssh')
    await ssh_worker.recv_from_client(data)
    

@sio.on(InEvent.SSH_RESIZE)
@ws_auth_required
async def resize_pty(sid, data):
    ssh_worker: SSHWorker = await ws_session.get(sid, 'ssh')
    ssh_worker.resize_pty(data['cols'], data['rows'])
