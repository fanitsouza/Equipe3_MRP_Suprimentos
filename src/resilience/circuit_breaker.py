from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum
import logging
from typing import TypeVar

from src.observability.severity import Severity
from src.observability.structured_logging import log_event


T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float | None = None,
        recovery_timeout_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
        logger: logging.Logger | None = None,
        name: str = "mrp_provider",
    ) -> None:
        timeout = (
            recovery_timeout_seconds if recovery_timeout is None else recovery_timeout
        )
        if failure_threshold < 1:
            raise ValueError("failure_threshold deve ser maior ou igual a 1")
        if timeout < 0:
            raise ValueError("recovery_timeout nao pode ser negativo")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = timeout
        self.recovery_timeout_seconds = timeout
        self._clock = clock
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_at: float | None = None

    def call(self, operation: Callable[[], T]) -> T:
        self._ensure_call_allowed()
        try:
            result = operation()
        except Exception:
            self._record_failure()
            raise

        self._record_success()
        return result

    def _ensure_call_allowed(self) -> None:
        if self.state != CircuitState.OPEN:
            return

        assert self.last_failure_at is not None
        elapsed = self._clock() - self.last_failure_at
        if elapsed >= self.recovery_timeout:
            self._transition_to(CircuitState.HALF_OPEN)
            return

        raise CircuitOpenError("Circuit breaker aberto para o Motor MRP")

    def _record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_at = self._clock()
        if self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def _record_success(self) -> None:
        self.failure_count = 0
        self.last_failure_at = None
        self._transition_to(CircuitState.CLOSED)

    def _transition_to(self, new_state: CircuitState) -> None:
        old_state = self.state
        self.state = new_state
        if old_state == new_state:
            return
        log_event(
            self.logger,
            level=Severity.WARNING if new_state == CircuitState.OPEN else Severity.INFO,
            event="circuit_state_changed",
            module="circuit_breaker",
            message="Circuit breaker mudou de estado",
            supplier=self.name,
            old_state=old_state.value,
            new_state=new_state.value,
            failure_count=self.failure_count,
        )
