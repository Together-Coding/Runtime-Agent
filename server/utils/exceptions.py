from server.utils.response import api_error_response


class MissingRequiredException(Exception):
    error = 'Missing required field'
    status_code = 400

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __str__(self):
        return f'`{self.field_name}` is required.'

    def response(self):
        return api_error_response(self.error, str(self), status_code=self.status_code)
