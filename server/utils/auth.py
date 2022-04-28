from typing import Optional

from fastapi import Header, HTTPException

from configs import global_settings


async def bridge_only(api_key: Optional[str] = Header(None, alias='X-API-KEY')):
    if not global_settings.SERVER_INIT:
        # Server is not initialized.
        raise HTTPException(
            status_code=400,
            detail={'type': 'Init Needed', 'msg': 'Server is not initialized.'}
        )
    elif not global_settings.BRIDGE_KEY:
        # Bridge key is empty
        global_settings.SERVER_INIT = False
        raise HTTPException(
            status_code=400,
            detail={'type': 'Init Error', 'msg': 'Server needs to be re-initialized.'}
        )
    elif not api_key:
        raise HTTPException(
            status_code=401,
            detail={'type': 'Authorization Failed', 'msg': 'You are not authorized.'}
        )
