import importlib

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from configs import global_settings
from server import routers
from server.utils.exceptions import MissingRequiredException
from server.websocket import create_websocket

app = FastAPI()
sio, sio_app = create_websocket(app)

origins = ['https://together-coding.com']
if global_settings.DEBUG:
    origins.extend([
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['X-API-KEY']
)

for router_mod in routers.__all__:
    router = importlib.import_module(f'.routers.{router_mod}', package=__name__)
    app.include_router(router.router)
