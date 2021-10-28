class RealtimeError(Exception):
    """
    Base realtime exception.
    """


class NotConnectedError(RealtimeError):
    """
    Raised when operations requiring a connection are executed when socket is not connected
    """

    def __init__(self, func_name: str):
        self.offending_func_name: str = func_name

    def __str__(self):
        return f"A WS connection has not been established. Ensure you call Socket.connect() before calling Socket.{self.offending_func_name}()"


class ConnectionFailedError(RealtimeError):
    """
    Raised when connecting to the Phoenix server fails.
    """
