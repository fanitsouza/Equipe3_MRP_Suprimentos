"""Executa a pipeline de MRP em modo recorrente / agendado."""

import os
import signal
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings
from src.logger import logger
from src.pipeline import executar_processo

_RUNNING = True


def _signal_handler(signum, frame):
    global _RUNNING
    logger.info("run_scheduled | Sinal de encerramento recebido (%s). Finalizando...", signum)
    _RUNNING = False


def main() -> None:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    interval_minutes = float(os.getenv("INTERVAL_MINUTES", "20"))
    interval_seconds = int(interval_minutes * 60)

    logger.info(
        "run_scheduled | Iniciando servico agendado de MRP a cada %.1f minutos (%d segundos).",
        interval_minutes,
        interval_seconds,
    )

    settings = get_settings()

    cycle = 1
    while _RUNNING:
        logger.info("run_scheduled | --- Iniciando Ciclo #%d ---", cycle)
        try:
            execution = executar_processo(settings)
            logger.info(
                "run_scheduled | Ciclo #%d concluido com sucesso. ID: %s | Relatorio: %s | Fallback: %s",
                cycle,
                execution.execution_id,
                execution.relatorio,
                execution.usou_fallback,
            )
        except Exception as exc:
            logger.exception("run_scheduled | Erro durante o Ciclo #%d: %s", cycle, exc)

        cycle += 1

        logger.info(
            "run_scheduled | Aguardando %d segundos ate a proxima execucao...",
            interval_seconds,
        )

        for _ in range(interval_seconds):
            if not _RUNNING:
                break
            time.sleep(1)

    logger.info("run_scheduled | Servico agendado finalizado.")


if __name__ == "__main__":
    main()
