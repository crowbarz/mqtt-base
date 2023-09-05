"""Event queue management."""
import logging
from datetime import datetime
from threading import Event
from typing import List

from .const import APP_NAME

_LOGGER = logging.getLogger(APP_NAME)


class AppEvent:
    """Application event class."""

    def __init__(self) -> None:
        _LOGGER.debug("queuing event %s", type(self).__name__)
        EventQueue.event_queue.append(self)
        EventQueue.event_flag.set()


class RefreshEvent(AppEvent):
    """Refresh interval event class. Raised by the main loop when refresh interval has elapsed."""

    def __init__(self) -> None:
        pass  ## do not add to event queue


class EventQueue:
    """Event queue."""

    event_flag = Event()
    event_queue: List[AppEvent] = []

    def wait(self, sleep_interval) -> None:
        """Wait for an event."""
        sleep_start = datetime.now()
        _LOGGER.debug("sleeping for %ds", sleep_interval)
        EventQueue.event_flag.wait(timeout=sleep_interval)
        _LOGGER.debug(
            "woke up after %ds", (datetime.now() - sleep_start).total_seconds()
        )

    def pop(self) -> AppEvent | None:
        """Pop an event from the event queue."""
        if EventQueue.event_queue:
            return EventQueue.event_queue.pop(0)
        return None

    def check(self) -> bool:
        """Check whether event queue has events."""
        if EventQueue.event_flag.is_set():
            EventQueue.event_flag.clear()
            return True
        return False
