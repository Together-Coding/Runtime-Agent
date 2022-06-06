import os
import requests
from fastapi.responses import PlainTextResponse
from fastapi import APIRouter, Depends, Header, dependencies, HTTPException
from pydantic import BaseModel

from configs import settings, global_settings, read_bridge_key
from server.utils import os_util
from server.utils.response import api_response
from server.utils.auth import bridge_only

router = APIRouter(prefix="/run")


class StartBody(BaseModel):
    target_ptc_id: int
    course_id: int
    lesson_id: int


@router.post('/start')
def start_run(body: StartBody, auth: str = Header(alias='Authorization', default='')):
    headers = {
        'Authorization': auth
    }
    
    url = settings.WS_URL + f"/api/{body.course_id}/{body.lesson_id}/{body.target_ptc_id}"
    resp = requests.post(url, json={
        'target_ptc_id': body.target_ptc_id,
    }, headers=headers)

    files = resp.json()
    print(files)

    DIR = settings.SSH_DEFAULT_DIR
    if not os.path.exists(DIR):
        os.mkdir(DIR)

    for f, content in files.items():
        if not f:
            continue

        dir = os.path.dirname(f)
        
        for _ in range(2):
            try:
                with open(os.path.join(DIR, f), 'wt') as fp:
                    fp.write(content)
                break
            except (FileNotFoundError, FileExistsError):
                if not os.path.exists(os.path.join(DIR, f)):
                    os.makedirs(os.path.join(DIR, dir))

    uname = settings.USERNAME
    os.system(f'chown -R {uname}:{uname} {DIR}')

    return PlainTextResponse(str(files))
