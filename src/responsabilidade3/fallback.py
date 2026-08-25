from __future__ import annotations

import logging
import time
from typing import Protocol

from .alerts import AlertSink, send_alert
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .models import MRPResult
from .severity import Severity
from .structured_logging import log_event


class MRPProvider(Protocol):
    def get_results(self) -> list[MRPResult]:
        ...


class StaticMRPProvider:
    def __init__(self, results: list[MRPResult]) -> None:
        self.results = results

    def get_results(self) -> list[MRPResult]:
        return list(self.results)


class FallbackMRPProvider:
    def __init__(
        self,
        primary: MRPProvider,
        fallback: MRPProvider,
        alert_sink: AlertSink,
        circuit_breaker: CircuitBreaker | None = None,
        logger: logging.Logger | None = None,
        execution_id: str | None = None,
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.alert_sink = alert_sink
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.logger = logger or logging.getLogger(__name__)
        self.execution_id = execution_id

    def get_results(self) -> list[MRPResult]:
        start = time.perf_counter()
        try:
            results = self.circuit_breaker.call(self.primary.get_results)
            log_event(
                self.logger,
                level=Severity.INFO,
                event="mrp_results_loaded",
                module="fallback",
                message="Resultados MRP carregados pelo provedor primario",
                execution_id=self.execution_id,
                duration_ms=int((time.perf_counter() - start) * 1000),
                row_count=len(results),
            )
            return results
        except CircuitOpenError as exc:
            return self._use_fallback("MRP_CIRCUIT_OPEN", str(exc))
        except Exception as exc:
            return self._use_fallback(
                "MRP_FALLBACK_ATIVADO",
                str(exc),
                error_type=type(exc).__name__,
            )

    def _use_fallback(
        self,
        code: str,
        reason: str,
        error_type: str | None = None,
    ) -> list[MRPResult]:
        log_event(
            self.logger,
            level=Severity.WARNING,
            event="mrp_fallback_used",
            module="fallback",
            message="Responsabilidade 3 usando dados mock/fallback do MRP",
            execution_id=self.execution_id,
            error_type=error_type or code,
            reason=reason,
        )
        send_alert(
            self.alert_sink,
            level=Severity.WARNING,
            code=code,
            message="Responsabilidade 3 operando com dados mock/fallback do MRP",
            context={"reason": reason},
            logger=self.logger,
            execution_id=self.execution_id,
        )
        return self.fallback.get_results()
