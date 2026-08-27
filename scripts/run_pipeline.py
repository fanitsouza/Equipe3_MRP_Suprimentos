"""Executa o processo completo e informa o relatório produzido."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings
from src.pipeline import executar_processo


def main() -> None:
    execution = executar_processo(get_settings())
    print(f"Execução: {execution.execution_id}")
    print(f"Relatório: {execution.relatorio}")
    print(f"Fallback utilizado: {execution.usou_fallback}")
    for item in execution.resultados:
        print(
            item.material,
            item.necessidade,
            item.quantidade_comprar,
            item.status_validacao,
        )


if __name__ == "__main__":
    main()
