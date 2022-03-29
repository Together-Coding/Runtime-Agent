from fastapi import FastAPI, Request

from server import routers
from server.utils import os_util
from server.utils.response import api_response, api_error_response
from server.utils.exceptions import MissingRequiredException

app = FastAPI()
app.include_router(routers.router)


@app.exception_handler(MissingRequiredException)
async def missing_required_exception_handler(request: Request, exc: MissingRequiredException):
    return exc.response()
