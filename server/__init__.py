import importlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs import global_settings
from server import routers
from server.websocket import create_websocket

app = FastAPI()
sio, sio_app = create_websocket(app)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['X-API-KEY', 'Authorization']
)

for router_mod in routers.__all__:
    router = importlib.import_module(f'.routers.{router_mod}', package=__name__)
    app.include_router(router.router)
