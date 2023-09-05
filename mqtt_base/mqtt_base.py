"""Event driven base framework for MQTT applications."""

import argparse
import logging
import signal
import traceback
import sys

import daemon
from daemon import pidfile

from .args import mqtt_add_args, mqtt_post_process_args
from .const import APP_NAME
from .exception import ExitApp
from .event import RefreshEvent, EventQueue
from .mqtt import MQTTClient, MQTTConnectEvent

_LOGGER = logging.getLogger(APP_NAME)


class MQTTBaseApp:
    APP_NAME = APP_NAME

    def __init__(self, args: dict):
        """Initialise MQTTBaseApp class."""
        self._event_queue = EventQueue()  ## Initialise event queue
        self._mqtt_client = MQTTClient(args)  ## Initialise MQTT client

        ## Base MQTT arguments
        self.mqtt_host: str = args["host"]
        self.mqtt_port: int = args["port"]
        self.mqtt_keepalive: int = args["keepalive"]

        self.mqtt_topic: str = args["topic"]
        self.mqtt_qos: int = args["qos"]
        self.mqtt_retain: bool = args["retain"]
        self.connect_timeout: int = args["connect_timeout"]
        self.refresh_interval: int = args["refresh_interval"]

    @classmethod
    def add_args(
        cls, parser: argparse.ArgumentParser | None = None
    ) -> argparse.ArgumentParser:
        """Generate MQTT argument parser. Override with app specific arguments.

        super().add_args() should be called by child class, either at start
        (parser = argparse.ArugmentParser) or end (parser = None).
        """
        return mqtt_add_args(parser)

    @classmethod
    def post_process_args(cls, args: dict) -> dict:
        """Perform post processing of args. Override with app specific processing.

        super().post_process_args() should be called by child class, either
        at start (parser = argparse.ArugmentParser) or end (parser = None).
        """
        return mqtt_post_process_args(args)

    def setup(self, args) -> None:
        """Set up app. Override with app specific setup as required."""
        _LOGGER.info("setting up %s: %s", self.APP_NAME, args)

    def handle_event(self, event):
        """Handle app event. Override with app event handling.

        - MQTTConnectEvent is passed when MQTT broker connection is
          successfully established.
        - RefreshEvent is passed when self.refresh_interval has elapsed since
          the previous event.
        """
        match event:
            case MQTTConnectEvent():
                pass
            case RefreshEvent():
                pass
            case _:
                _LOGGER.error("unknown event type %s", type(event).__name__)

    def shutdown(self):
        """Shut down app. Override with app specific shutdown."""
        _LOGGER.info("shutting down %s", self.APP_NAME)

    def publish_mqtt(self, topic: str, payload: str, qos: int, retain: bool) -> bool:
        """Publish the contents of a file to the MQTT broker."""
        self._mqtt_client.publish(topic, payload, qos, retain)

    def get_refresh_interval(self) -> float:
        """Calculate next refresh interval."""
        return self.refresh_interval

    def _main_loop(self):
        """Main application loop."""

        ## Connect to MQTT broker
        mqtt_client = self._mqtt_client
        _LOGGER.info("connecting to MQTT broker %s:%d", self.mqtt_host, self.mqtt_port)
        mqtt_client.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive)

        mqtt_connected = False
        event_queue = self._event_queue
        sleep_interval = self.connect_timeout  # on initial connect

        while True:
            event_queue.wait(sleep_interval)
            if event_queue.check():
                while event := event_queue.pop():
                    _LOGGER.debug("processing event %s", type(event).__name__)
                    match event:
                        case MQTTConnectEvent():
                            if event.rc == 0:
                                mqtt_connected = True
                                self.handle_event(event)
                        case _:
                            self.handle_event(event)
            elif mqtt_connected:  ## waited for refresh_interval
                _LOGGER.debug("triggering RefreshEvent")
                self.handle_event(RefreshEvent())
            else:
                raise Exception("connection to MQTT broker timed out")
            sleep_interval = self.get_refresh_interval()

    def _shutdown(self):
        """Initiate shutdown of the application."""
        self.shutdown()

        if self._mqtt_client:
            self._mqtt_client.shutdown()

    @staticmethod
    def _setup_logging(log_level_count: int, logfile: str | None):
        log_level = logging.WARNING
        log_level_name = "default"
        if log_level_count >= 2:
            log_level = logging.DEBUG
            log_level_name = "debug"
        elif log_level_count >= 1:
            log_level = logging.INFO
            log_level_name = "info"

        ## Enable logging
        log_format = "%(asctime)s %(levelname)s: %(message)s"
        log_format_color = "%(log_color)s" + log_format
        date_format = "%Y-%m-%d %H:%M:%S"
        try:
            import colorlog

            colorlog.basicConfig(
                filename=logfile,
                level=log_level,
                format=log_format_color,
                datefmt=date_format,
            )
        except:
            logging.basicConfig(
                filename=logfile,
                level=log_level,
                format=log_format,
                datefmt=date_format,
            )
        _LOGGER.info("setting log level to %s", log_level_name)

    @classmethod
    def main(cls):
        """Entrypoint to main application. Call via class."""
        ## Parse application arguments
        parser = cls.add_args(None)
        args = vars(parser.parse_args())
        args = cls.post_process_args(args)

        ## Instantiate application class
        try:
            app = cls(args)
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
            exit(255)

        debug = args["debug"]
        logfile = args["logfile"]

        def sigterm_handler(_signal, _frame):
            _LOGGER.warning("SIGTERM received, exiting")
            raise ExitApp(0)

        def start():
            """Set up application and start main loop."""
            try:
                rc = 0
                signal.signal(signal.SIGTERM, sigterm_handler)

                app.setup(args)
                app._main_loop()
            except KeyboardInterrupt:
                _LOGGER.warning("Keyboard interrupt, exiting")
            except ExitApp as exc:
                rc = exc.rc
            except Exception as exc:
                _LOGGER.error("Exception: %s", exc)
                print(f"Exception: {exc}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                rc = 255
            finally:
                app._shutdown()
            exit(rc)

        if args["daemon"]:
            ## Start application as daemon
            pid_file = args["pidfile"]
            pid_lock = pidfile.TimeoutPIDLockFile(pid_file) if pid_file else None
            with daemon.DaemonContext(pidfile=pid_lock):
                MQTTBaseApp._setup_logging(debug, logfile)
                _LOGGER.info("starting %s as daemon", cls.APP_NAME)
                start()
        else:
            MQTTBaseApp._setup_logging(debug, logfile)
            start()


def main():
    MQTTBaseApp.main()


if __name__ == "__main__":
    main()
