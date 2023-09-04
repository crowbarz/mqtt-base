"""mqtt_base argument parsing."""

import argparse
from typing import Any

from .const import (
    VERSION,
    DEF_MQTT_HOST,
    DEF_MQTT_PORT,
    DEF_MQTT_PORT_TLS,
    DEF_CONNECT_TIMEOUT,
    DEF_INOTIFY_TRIGGER_DELAY,
    DEF_INOTIFY_RESTART_DELAY,
    DEF_DEBUG_LEVEL,
)


## https://stackoverflow.com/questions/14117415/in-python-using-argparse-allow-only-positive-integers
def check_positive_int(value: Any) -> int:
    """ArgParse parser to check that a positive integer value has been specified."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s not an integer" % value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def mqtt_add_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Parse command line arguments."""
    if parser is None:
        parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument(
        "-H",
        "--host",
        default=DEF_MQTT_HOST,
        help="Hostname for the MQTT broker",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=check_positive_int,
        default=None,
        help="Port for the MQTT broker",
    )
    parser.add_argument(
        "--connect-timeout",
        type=check_positive_int,
        default=DEF_CONNECT_TIMEOUT,
        help="Timeout for initial connection to MQTT broker",
    )
    parser.add_argument(
        "--max-reconnect-delay",
        type=check_positive_int,
        default=0,
        help="Set maximum broker reconnect delay (in seconds)",
    )
    parser.add_argument(
        "-u",
        "--username",
        default=None,
        help="Username to authenticate with MQTT broker",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=None,
        help="Password to authenticate with MQTT broker",
    )
    parser.add_argument(
        "--password-file", default=None, help="Path to file to read password from"
    )
    parser.add_argument(
        "-c",
        "--client-id",
        default=None,
        help="Client ID to use when connecting to MQTT broker",
    )
    parser.add_argument(
        "-C",
        "--clean-session",
        action="store_false",
        default=True,
        help="Set MQTT retain flag for published message",
    )
    parser.add_argument(
        "-t",
        "--topic",
        required=True,
        help="MQTT topic for published message",
    )
    parser.add_argument(
        "--payload-file-missing",
        default=None,
        help="MQTT payload to publish if file is not found",
    )
    parser.add_argument(
        "-q",
        "--qos",
        choices=range(0, 3),
        type=int,
        default=0,
        help="MQTT QoS for published message",
    )
    parser.add_argument(
        "-R",
        "--retain",
        action="store_true",
        default=False,
        help="Set MQTT retain flag for published message",
    )
    parser.add_argument(
        "--keepalive",
        default=65,
        type=check_positive_int,
        help="Set the keepalive interval for the MQTT client",
    )
    parser.add_argument(
        "--tls",
        action="store_true",
        default=False,
        help="Enable SSL/TLS support",
    )
    parser.add_argument(
        "--tls-insecure",
        default=False,
        help="Disable certificate verification. Not recommended",
    )
    parser.add_argument(
        "--ca-certs",
        default=None,
        help="Path to the Certificate Authority certificate files that are to be treated as trusted",
    )
    parser.add_argument(
        "--certfile",
        default=None,
        help="Path to the PEM encoded client certificate for authentication with the broker",
    )
    parser.add_argument(
        "--keyfile",
        default=None,
        help="Path to the private keys for authentication with the broker",
    )
    parser.add_argument(
        "--birth-topic",
        default=None,
        help="Set a birth topic to be sent to the broker",
    )
    parser.add_argument(
        "--birth-payload",
        default=None,
        help="Set a birth payload to be sent to the broker",
    )
    parser.add_argument(
        "--birth-qos",
        choices=range(0, 3),
        type=int,
        default=0,
        help="Set the QoS for the birth payload",
    )
    parser.add_argument(
        "--birth-retain",
        action="store_true",
        default=False,
        help="Set retain flag for the birth payload",
    )
    parser.add_argument(
        "--will-topic",
        default=None,
        help="Set a will topic to be sent to the broker",
    )
    parser.add_argument(
        "--will-payload",
        default=None,
        help="Set a will payload to be sent to the broker",
    )
    parser.add_argument(
        "--will-qos",
        choices=range(0, 3),
        type=int,
        default=0,
        help="Set the QoS for the will payload",
    )
    parser.add_argument(
        "--will-retain",
        action="store_true",
        default=False,
        help="Set retain flag for the will payload",
    )
    parser.add_argument(
        "--daemon",
        default=False,
        action="store_true",
        help="Run application as a daemon",
    )
    parser.add_argument(
        "--pidfile",
        default=None,
        help="File to store PID when running as a daemon",
    )
    parser.add_argument(
        "--refresh-interval",
        default=60,
        type=check_positive_int,
        help="Set the interval for republishing with current content",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=DEF_DEBUG_LEVEL,
        type=check_positive_int,
        help="Set application debug level",
    )
    parser.add_argument(
        "--logfile",
        default=None,
        help="File to log messages to",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + VERSION,
        help="Show application version",
    )
    return parser


def mqtt_post_process_args(args: dict) -> dict:
    """Default post processing of arguments."""
    if not args["port"]:
        args["port"] = DEF_MQTT_PORT_TLS if args["tls"] else DEF_MQTT_PORT
    return args
