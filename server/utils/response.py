import flask as fl


def api_response(data: dict = None, status_code: int = 200):
    if not data:
        data = {}
    return fl.jsonify(data), status_code


def api_error_response(error: str, message: str, data: dict = None, status_code: int = 200):
    if not data:
        data = {}

    data['error'] = error
    data['message'] = message
    return fl.jsonify(data), status_code
