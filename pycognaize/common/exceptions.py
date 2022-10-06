class DrawOnShellException(Exception):
    pass


class ServerAPIException(Exception):
    def __init__(self, failure_reason: str = ''):
        message = f"Connection failed due to {failure_reason}"
        super().__init__(message)
