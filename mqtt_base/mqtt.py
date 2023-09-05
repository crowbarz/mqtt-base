"""MQTT client class."""
import logging
from pathlib import Path

import paho.mqtt.client as mqtt

from .const import APP_NAME
from .event import AppEvent

_LOGGER = logging.getLogger(APP_NAME)


class MQTTConnectEvent(AppEvent):
    """Event class for MQTT broker connect event."""

    def __init__(self, flags, rc: int) -> None:
        self.flags = flags
        self.rc = rc
        super().__init__()


class MQTTClient:
    """MQTT client used to publish messages to MQTT broker."""

    def __init__(self, args: dict) -> None:
        ## Create MQTT client
        self.client = mqtt.Client(client_id=args["client_id"])
        self.connected = False

        if args["tls"]:
            _LOGGER.info("enabling TLS")
            self.client.tls_set(
                ca_certs=args["ca_certs"],
                certfile=args["certfile"],
                keyfile=args["keyfile"],
            )
        if username := args["username"]:
            password = args["password"]
            password_file = args["password_file"]
            if not password and password_file:
                try:
                    password = Path(password_file).read_text().rstrip()
                except Exception as exc:
                    raise Exception(f"cannot read password file: {exc}") from exc
            self.client.username_pw_set(username, password)

        self.birth_msg = None
        if birth_topic := args["birth_topic"]:
            self.birth_msg = {
                "birth_topic": birth_topic,
                "birth_payload": args["birth_payload"],
                "birth_qos": args["birth_qos"],
                "birth_retain": args["birth_retain"],
            }
        if will_topic := args["will_topic"]:
            _LOGGER.info("enabling will message on MQTT broker")
            self.client.will_set(
                will_topic,
                args["will_payload"],
                args["will_qos"],
                args["will_retain"],
            )

        if max_reconnect_delay := args["max_reconnect_delay"]:
            self.client.reconnect_delay_set(max_delay=max_reconnect_delay)

    def shutdown(self) -> None:
        """Shut down the MQTT client."""
        if self.client:
            self.client.loop_stop()

    def connect(self, host: str, port: int, keepalive: int) -> None:
        """Connect client to MQTT broker."""
        self.client.enable_logger(_LOGGER)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        try:
            self.client.connect(host, port, keepalive=keepalive)
        except Exception as exc:
            raise Exception(f"connection to MQTT broker failed: {exc}") from exc

        self.client.loop_start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc: int) -> None:
        """Callback to process MQTT client connect event."""
        if rc > 0:
            _LOGGER.error(
                "connection to MQTT broker failed: %s", mqtt.connack_string(rc)
            )
        else:
            self.connected = True
            _LOGGER.info("connection to MQTT broker established")

            ## Publish birth message
            if self.birth_msg:
                _LOGGER.info("publishing birth message")
                self.client.publish(
                    self.birth_msg["birth_topic"],
                    self.birth_msg["birth_payload"],
                    self.birth_msg["birth_qos"],
                    self.birth_msg["birth_retain"],
                )
        MQTTConnectEvent(flags, rc)

    def on_disconnect(self, client: mqtt.Client, userdata, rc: int) -> None:
        """Callback to process MQTT client disconnect event."""
        if rc > 0:
            _LOGGER.warning(
                "disconnected from MQTT broker: %s", mqtt.connack_string(rc)
            )
        ## Ignore disconnect event and let client reconnect
        # MQTTConnectEvent(None, rc)

    def publish(self, topic: str, payload: str, qos: int, retain: bool) -> bool:
        """Publish the contents of a file to the MQTT broker."""
        try:
            _LOGGER.debug("publishing msg %s: %s", topic, payload)
            msg = self.client.publish(topic, payload, qos, retain)
            # msg.wait_for_publish()
            if msg.rc > 0:
                _LOGGER.error("error publishing message: %s", mqtt.error_string(msg.rc))
                return False
            return True
        except ValueError as exc:
            _LOGGER.error("invalid MQTT message: Error %d: %s", msg.rc, exc)
            return False
        except RuntimeError as exc:
            _LOGGER.error("could not publish to MQTT broker: %s", exc)
            return False
