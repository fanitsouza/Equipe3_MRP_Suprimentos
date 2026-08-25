"""Responsabilidade 3: relatorios, logs e alertas sobre resultados MRP.

Esta camada comeca depois que o Motor MRP ja calculou os resultados.
"""

from .adapter import AdapterError, adapt_mrp_records
from .alerts import Alert, InMemoryAlertSink, JsonLinesAlertSink, send_alert
from .circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from .fallback import FallbackMRPProvider, StaticMRPProvider
from .input_contract import (
    ContractValidationError,
    MRPInputContract,
    MRPInputContractDict,
)
from .models import MRPResult, MRPResultDict
from .report import REPORT_HEADERS, ReportGenerationError, generate_excel_report
from .severity import Severity
from .structured_logging import log_event

__all__ = [
    "AdapterError",
    "Alert",
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "ContractValidationError",
    "FallbackMRPProvider",
    "InMemoryAlertSink",
    "JsonLinesAlertSink",
    "MRPInputContract",
    "MRPInputContractDict",
    "MRPResult",
    "MRPResultDict",
    "REPORT_HEADERS",
    "ReportGenerationError",
    "Severity",
    "StaticMRPProvider",
    "adapt_mrp_records",
    "generate_excel_report",
    "log_event",
    "send_alert",
]
