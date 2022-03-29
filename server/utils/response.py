from fastapi.responses import JSONResponse


def api_response(data: dict = None, status_code: int = 200):
    if not data:
        data = {}
    return JSONResponse(status_code=status_code,
                        content=data)


def api_error_response(error: str, message: str, data: dict = None, status_code: int = 200):
    if not data:
        data = {}

    data['error'] = error
    data['message'] = message
    return JSONResponse(status_code=status_code,
                        content=data)
