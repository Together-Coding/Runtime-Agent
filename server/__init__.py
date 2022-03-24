import flask as fl
from flask import Flask

from server.utils import os_util
from server.utils.response import api_response, api_error_response
from server.utils.exceptions import MissingRequiredException

import configs

app = Flask(__name__)
app.config.from_object(configs)

from server.views import init as init_view

init_view(app)


@app.errorhandler(405)
def error_405(e):
    return api_error_response('Method not allowed',
                              f'{fl.request.method} method is not allowed for {fl.request.path}',
                              status_code=405)
