import importlib

from fastapi import FastAPI, Request

from server import routers
from server.utils import os_util
from server.utils.response import api_response, api_error_response
from server.utils.exceptions import MissingRequiredException
from server.websocket import create_websocket

app = FastAPI()
sio, sio_app = create_websocket(app)

for router_mod in routers.__all__:
    router = importlib.import_module(f'.routers.{router_mod}', package=__name__)
    app.include_router(router.router)


@app.exception_handler(MissingRequiredException)
async def missing_required_exception_handler(request: Request, exc: MissingRequiredException):
    return exc.response()
