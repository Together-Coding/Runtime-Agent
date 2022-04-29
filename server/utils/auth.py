from typing import Optional

from fastapi import Header, HTTPException

from configs import global_settings


async def bridge_only(api_key: Optional[str] = Header(None, alias='X-API-KEY')):
    """
    X-API-KEY is required. The only subject that knows API key is a Bridge server.
    In order to check API key, this(Agent) server must be initialized first.

    When this server is initialized, api key is saved into config, named `BRIDGE_KEY`, 
    api key is in header `X-API-KEY`, and the api key is same with `BRIDGE_KEY`,
    then the request is authorized.
    """
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
        # API key is missing
        raise HTTPException(
            status_code=401,
            detail={'type': 'Authorization Failed', 'msg': 'X-API-KEY is missing'}
        )
    elif api_key != global_settings.BRIDGE_KEY:
        # API key is mismatched
        raise HTTPException(
            status_code=401,
            detail={'type': 'Authorization Failed', 'msg': 'Not authorized key'}
        )