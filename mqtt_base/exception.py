"""mqtt_base exceptions."""


class ExitApp(Exception):
    """Exception for exiting the application."""

    def __init__(self, rc: int = 0):
        self.rc = rc
