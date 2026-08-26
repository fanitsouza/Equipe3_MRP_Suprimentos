from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from .severity import Severity, normalize_severity


SENSITIVE_KEYS = {
    "senha",
    "password",
    "token",
    "cookie",
    "segredo",
    "secret",
    "credential",
    "credentials",
    "credenciais",
}


def log_event(
    logger: logging.Logger,
    level: Severity | str,
    event: str,
    module: str,
    message: str,
    execution_id: str | None = None,
    supplier: str | None = None,
    error_type: str | None = None,
    duration_ms: int | None = None,
    **context: Any,
) -> dict[str, Any]:
    severity = normalize_severity(level)
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": severity.value,
        "event": event,
        "module": module,
        "message": message,
    }
    optional_fields = {
        "execution_id": execution_id,
        "supplier": supplier,
        "error_type": error_type,
        "duration_ms": duration_ms,
    }
    payload.update(
        {key: value for key, value in optional_fields.items() if value is not None}
    )

    safe_context = sanitize_context(context)
    if safe_context:
        payload["context"] = safe_context

    logger.log(_LOGGING_LEVELS[severity], json.dumps(payload, ensure_ascii=False))
    return payload


def sanitize_context(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if _is_sensitive_key(key) else sanitize_context(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_context(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_context(item) for item in value)
    return value


def _is_sensitive_key(key: Any) -> bool:
    normalized = str(key).strip().lower()
    return any(sensitive in normalized for sensitive in SENSITIVE_KEYS)


_LOGGING_LEVELS = {
    Severity.INFO: logging.INFO,
    Severity.AVISO: logging.WARNING,
    Severity.ERRO: logging.ERROR,
    Severity.CRITICO: logging.CRITICAL,
}
