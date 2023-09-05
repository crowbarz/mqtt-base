"""mqtt_base exceptions."""


class ExitApp(Exception):
    """Exception for exiting the application."""

    def __init__(self, rc: int = 0) -> None:
        self.rc = rc
