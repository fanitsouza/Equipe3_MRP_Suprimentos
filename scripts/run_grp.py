"""Executa manualmente apenas a automação do GRP Web."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.collectors.grp_web import collect_grp_web
from src.config import get_settings


def main() -> None:
    settings = get_settings()
    records = collect_grp_web(
        settings.grp_url,
        settings.grp_user,
        settings.grp_password,
        headless=False,
    )
    for record in records:
        print(
            f"{record.supplier} | {record.material} | "
            f"capacidade: {record.capacity} | "
            f"prazo: {record.lead_time_days} dias | preço: {record.unit_price}"
        )
    print(f"Total de registros: {len(records)}")


if __name__ == "__main__":
    main()
