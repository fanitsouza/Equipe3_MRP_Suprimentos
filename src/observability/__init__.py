"""Logs estruturados e mecanismos de alerta."""

from .alerts import Alert, InMemoryAlertSink, JsonLinesAlertSink, send_alert
from .severity import Severity
from .structured_logging import log_event

__all__ = [
    "Alert",
    "InMemoryAlertSink",
    "JsonLinesAlertSink",
    "Severity",
    "log_event",
    "send_alert",
]
