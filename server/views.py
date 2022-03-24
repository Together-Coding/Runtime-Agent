import flask as fl
from flask import Flask, Blueprint

from server.utils import os_util
from server.utils.response import api_response, api_error_response

bp = Blueprint('main', __name__, url_prefix='/')

# FIXME
TEMP_DB = {}


def init(app: Flask):
    app.register_blueprint(bp)


@bp.route('/ping')
def pong():
    # IP address ?
    # Docker image information ?
    # Available languages?

    return api_response({
        'ping': 'pong',
    })


@bp.route('/init')
def init_server():
    """
    TODO
    Initialize server at the first time this server is up.
    The Runtime Bridge server will call this.
    """

    return api_response()


@bp.route('/execute')
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


@bp.route('/execute/suspend')
def suspend_execution():
    """
    TODO
    Pre-suspension processes. This endpoint is called before suspension.

    Steps
    1. ...
    """

    return api_response({})
