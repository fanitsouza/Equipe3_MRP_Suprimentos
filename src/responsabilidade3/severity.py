from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def normalize_severity(value: Severity | str) -> Severity:
    if isinstance(value, Severity):
        return value
    try:
        return Severity(str(value).upper())
    except ValueError as exc:
        raise ValueError(f"Nivel de severidade invalido: {value!r}") from exc
