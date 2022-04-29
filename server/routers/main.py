from fastapi import APIRouter, Depends, dependencies, HTTPException
from pydantic import BaseModel

from configs import settings, global_settings, read_bridge_key
from server.utils import os_util
from server.utils.response import api_response
from server.utils.auth import bridge_only

router = APIRouter()


@router.get('/ping')
def pong():
    return api_response({
        'ping': 'pong',
        'init': global_settings.SERVER_INIT,
        'key_status': bool(global_settings.BRIDGE_KEY),
    })


class InitBody(BaseModel):
    api_key: str


@router.post('/init')
def init_server(body: InitBody):
    """
    Initialize server at the first time this server is up.
    The Runtime Bridge server will call this path.
    """

    # If already initialized, return error
    if global_settings.SERVER_INIT is True:
        raise HTTPException(
            status_code=400,
            detail={
                'type': 'Init Error',
                'msg': 'Server is already initialized.'
            })

    # Save API key into `bridge_key` file. It's ok to save it like this because
    # it is only applicable to this server.
    with open(global_settings.BRIDGE_KEY_NAME, 'wt') as fp:
        fp.write(body.api_key)
    read_bridge_key()

    # Change user password randomly.
    pw = os_util.change_password()

    # Set as initialized
    global_settings.SERVER_INIT = True

    return api_response({
        'username': settings.USERNAME,
        'auth_type': 'password',
        'auth': pw
    })


@router.post('/execute', dependencies=[Depends(bridge_only)])
def execute_command():
    """
    TODO
    Execute pre-execution processes. This endpoint is called before execution of codes.

    Steps
    1. Clear app directory
    2. Download user's project codes from DB
    3. Execute pre-execute processes
        e.g. install packages
    """

    return api_response({})


@router.post('/execute/suspend', dependencies=[Depends(bridge_only)])
def suspend_execution():
    """
    TODO
    Pre-suspension processes. This endpoint is called before suspension.

    Steps
    1. ...
    """

    return api_response({})
