"""Orquestração do fluxo principal da automação."""

from src.collectors.pipeline import collect_all
from src.config import Settings
from src.logger import logger
from src.mrp.integration import calcular_mrp_da_coleta
from src.mrp.models import ResultadoMRP


def executar_mrp(settings: Settings) -> list[ResultadoMRP]:
    """Executa coleta, validações cruzadas e cálculo do MRP."""
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

