class DrawOnShellException(Exception):
    pass


class AWS_connection_exception(Exception):
    def __init__(self):
        message = "AWS connection failed"
        super().__init__(message)
