"""Orquestração ponta a ponta da automação de suprimentos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from src.collectors.pipeline import collect_all
from src.config import Settings
from src.logger import logger
from src.mrp.integration import calcular_mrp_da_coleta
from src.mrp.models import ResultadoMRP
from src.observability import JsonLinesAlertSink, Severity, log_event, send_alert
from src.reporting import MRPInputContract, adapt_engine_results, generate_excel_report
from src.resilience import (
    CircuitBreaker,
    FallbackMRPProvider,
    JsonMRPProvider,
    save_mrp_cache,
)


@dataclass(frozen=True)
class ResultadoExecucao:
    execution_id: str
    resultados: list[MRPInputContract]
    relatorio: Path
    usou_fallback: bool


class _LiveMRPProvider:
    def __init__(self, settings: Settings, cache_path: Path) -> None:
        self.settings = settings
        self.cache_path = cache_path

    def get_results(self) -> list[MRPInputContract]:
        coleta = collect_all(self.settings)
        resultados = calcular_mrp_da_coleta(coleta)
        adaptados = adapt_engine_results(resultados, coleta["stock"])
        save_mrp_cache(adaptados, self.cache_path)
        return adaptados


_PIPELINE_BREAKER = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout_seconds=60,
    logger=logger,
    name="fontes_mrp",
)


def executar_mrp(settings: Settings) -> list[ResultadoMRP]:
    """Executa somente coleta e motor, mantido para compatibilidade."""
    logger.info("pipeline_mrp | Iniciando coleta e cálculo.")
    coleta = collect_all(settings)
    resultados = calcular_mrp_da_coleta(coleta)
    pendencias = sum(item.requer_validacao_humana for item in resultados)
    logger.info(
        "pipeline_mrp | %d materiais calculados; %d pendências humanas.",
        len(resultados),
        pendencias,
    )
    return resultados


def executar_processo(
    settings: Settings,
    circuit_breaker: CircuitBreaker | None = None,
) -> ResultadoExecucao:
    """Executa coleta, MRP, fallback, alertas e relatório Excel."""
    execution_id = str(uuid4())
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = settings.output_dir / "ultimo_mrp_valido.json"
    report_path = settings.output_dir / "relatorio_necessidades.xlsx"
    alert_sink = JsonLinesAlertSink(settings.alert_file)
    breaker = circuit_breaker or _PIPELINE_BREAKER
    provider = FallbackMRPProvider(
        primary=_LiveMRPProvider(settings, cache_path),
        fallback=JsonMRPProvider(cache_path),
        alert_sink=alert_sink,
        circuit_breaker=breaker,
        logger=logger,
        execution_id=execution_id,
    )

    log_event(
        logger,
        Severity.INFO,
        "pipeline_started",
        "pipeline",
        "Execução ponta a ponta iniciada",
        execution_id=execution_id,
    )
    failures_before = breaker.failure_count
    resultados = provider.get_results()
    usou_fallback = breaker.failure_count > failures_before or breaker.state.value == "open"

    for item in resultados:
        if item.status_validacao == "AGUARDANDO_VALIDACAO_HUMANA":
            send_alert(
                alert_sink,
                Severity.WARNING,
                "Item bloqueado para validação humana antes da compra",
                context={"material": item.material, "fornecedor": item.fornecedor},
                code="VALIDACAO_HUMANA_NECESSARIA",
                logger=logger,
                execution_id=execution_id,
            )

    relatorio = generate_excel_report(
        resultados,
        output_path=report_path,
        template_path=settings.source_dir / "modelo_relatorio_necessidades.xlsx",
        logger=logger,
        execution_id=execution_id,
    )
    log_event(
        logger,
        Severity.INFO,
        "pipeline_finished",
        "pipeline",
        "Execução ponta a ponta concluída",
        execution_id=execution_id,
        row_count=len(resultados),
        used_fallback=usou_fallback,
        report_path=str(relatorio),
    )
    return ResultadoExecucao(execution_id, resultados, relatorio, usou_fallback)

