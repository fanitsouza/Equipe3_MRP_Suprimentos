from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    INFO = "INFO"
    AVISO = "AVISO"
    ERRO = "ERRO"
    CRITICO = "CRÍTICO"

    WARNING = "AVISO"
    ERROR = "ERRO"
    CRITICAL = "CRÍTICO"


def normalize_severity(value: Severity | str) -> Severity:
    if isinstance(value, Severity):
        return value
    normalized = str(value).upper()
    aliases = {
        "WARNING": Severity.AVISO,
        "ERROR": Severity.ERRO,
        "CRITICAL": Severity.CRITICO,
        "CRITICO": Severity.CRITICO,
    }
    try:
        return aliases[normalized] if normalized in aliases else Severity(normalized)
    except ValueError as exc:
        raise ValueError(f"Nivel de severidade invalido: {value!r}") from exc
