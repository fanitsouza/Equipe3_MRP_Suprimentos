"""Adaptação e geração do relatório final do MRP."""

from .adapter import AdapterError, adapt_engine_results, adapt_mrp_records
from .excel import REPORT_HEADERS, ReportGenerationError, generate_excel_report
from .models import (
    ContractValidationError,
    MRPInputContract,
    MRPInputContractDict,
)

MRPResult = MRPInputContract
MRPResultDict = MRPInputContractDict

__all__ = [
    "AdapterError",
    "ContractValidationError",
    "MRPInputContract",
    "MRPInputContractDict",
    "MRPResult",
    "MRPResultDict",
    "REPORT_HEADERS",
    "ReportGenerationError",
    "adapt_engine_results",
    "adapt_mrp_records",
    "generate_excel_report",
]
