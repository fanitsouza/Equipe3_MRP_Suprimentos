"""Executa manualmente todos os coletores para diagnóstico."""

import sys
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.collectors.pipeline import collect_all
from src.config import get_settings


def main() -> None:
    result = collect_all(get_settings())
    for name, value in result.items():
        print(f"\n=== {name.upper()} ===")
        pprint(value)


if __name__ == "__main__":
    main()
