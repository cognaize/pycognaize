class DrawOnShellException(Exception):
    pass


class ServerAPIException(Exception):
    def __init__(self, failure_reason: str = ''):
        message = f"Connection failed due to {failure_reason}"
        super().__init__(message)


class AuthenthicationError(Exception):
    def __init__(self):
        message = "Please login to access a remote Snapshot"
        super().__init__(message)
