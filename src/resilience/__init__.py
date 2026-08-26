"""Fallback e Circuit Breaker para fontes externas."""

from .circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from .fallback import FallbackMRPProvider, JsonMRPProvider, StaticMRPProvider, save_mrp_cache

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "FallbackMRPProvider",
    "JsonMRPProvider",
    "StaticMRPProvider",
    "save_mrp_cache",
]
