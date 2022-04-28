class MissingRequiredException(Exception):
    error = 'Missing required field'
    status_code = 400

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __str__(self):
        return f'`{self.field_name}` is required.'


class SSHStopRetryException(Exception):
    pass


class SSHConnectionException(Exception):
    pass
