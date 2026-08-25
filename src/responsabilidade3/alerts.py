from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .severity import Severity, normalize_severity
from .structured_logging import log_event, sanitize_context


@dataclass(frozen=True, slots=True)
class Alert:
    code: str
    message: str
    level: Severity | str = Severity.WARNING
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "level", normalize_severity(self.level).value)
        object.__setattr__(self, "context", sanitize_context(self.context))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AlertSink(Protocol):
    def publish(self, alert: Alert) -> None:
        ...


class InMemoryAlertSink:
    def __init__(self) -> None:
        self.alerts: list[Alert] = []

    def publish(self, alert: Alert) -> None:
        self.alerts.append(alert)


class JsonLinesAlertSink:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def publish(self, alert: Alert) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(alert.to_dict(), ensure_ascii=False) + "\n")


def send_alert(
    sink: AlertSink,
    level: Severity | str,
    message: str,
    context: dict[str, Any] | None = None,
    code: str = "RESP3_ALERT",
    logger: logging.Logger | None = None,
    execution_id: str | None = None,
) -> Alert:
    alert = Alert(
        code=code,
        message=message,
        level=level,
        context=context or {},
    )
    sink.publish(alert)

    if logger is not None:
        log_event(
            logger,
            level=alert.level,
            event="alert_sent",
            module="alerts",
            message=message,
            execution_id=execution_id,
            error_type=code,
            **alert.context,
        )

    return alert
