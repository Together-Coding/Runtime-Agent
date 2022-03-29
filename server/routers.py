from fastapi import APIRouter

from server.utils import os_util
from server.utils.response import api_response

router = APIRouter()

# TODO 어떤 인증을 거쳐서 bridge 로부터
#  "이 서버에서만 사용할 임시 키"를 받아서 사용하는게 더 안전할 듯

# FIXME
TEMP_DB = {}


@router.get('/ping')
def pong():
    # Return useful values depending on its platform (local/container/...)
    # IP address ?
    # Docker image information ?
    # Available languages?

    return api_response({
        'ping': 'pong',
    })


@router.post('/init')
def init_server():
    """
    TODO
    Initialize server at the first time this server is up.
    The Runtime Bridge server will call this.
    """

    pw = os_util.change_password()

    return api_response({
        'pw': pw
    })


@router.post('/execute')
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


@router.post('/execute/suspend')
def suspend_execution():
    """
    TODO
    Pre-suspension processes. This endpoint is called before suspension.

    Steps
    1. ...
    """

    return api_response({})
