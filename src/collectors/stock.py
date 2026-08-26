from pathlib import Path

import pandas as pd

from src.models.data import StockRecord


REQUIRED_COLUMNS = {
    "Codigo_Material",
    "Estoque_Atual",
    "Demanda_Semanal",
    "Estoque_Seguranca",
}


def collect_stock(path: Path) -> list[StockRecord]:
    if not path.exists():
        raise FileNotFoundError(
            f"Planilha de estoque não encontrada: {path}"
        )

    try:
        df = pd.read_excel(path)
    except Exception as exc:
        raise ValueError(
            f"Não foi possível ler a planilha de estoque: {exc}"
        ) from exc

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            "Planilha de estoque inválida. "
            "Colunas ausentes: "
            + ", ".join(sorted(missing))
        )

    records = []

    for index, row in df.iterrows():
        line = index + 2

        material = str(row["Codigo_Material"]).strip()

        if not material or material.lower() == "nan":
            raise ValueError(
                f"Linha {line}: Codigo_Material vazio."
            )

        values = []

        for column in [
            "Estoque_Atual",
            "Demanda_Semanal",
            "Estoque_Seguranca",
        ]:
            try:
                value = float(row[column])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Linha {line}: valor inválido em {column}: "
                    f"{row[column]!r}"
                )

            if value < 0:
                raise ValueError(
                    f"Linha {line}: {column} não pode ser negativo."
                )

            values.append(value)

        records.append(
            StockRecord(
                material=material,
                stock=values[0],
                weekly_demand=values[1],
                safety_stock=values[2],
            )
        )

    return records
