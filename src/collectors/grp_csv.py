from pathlib import Path

import pandas as pd

from src.models.data import SupplierRecord


REQUIRED_COLUMNS = {
    "Fornecedor",
    "Material",
    "Capacidade_Semanal",
    "Prazo_Dias",
    "Preco_Unitario",
    "Status",
}


def collect_supplier_csv(path: Path) -> list[SupplierRecord]:
    if not path.exists():
        raise FileNotFoundError(
            f"CSV de fornecedores não encontrado: {path}"
        )

    try:
        df = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig"
        )
    except Exception as exc:
        raise ValueError(
            f"Não foi possível ler o CSV do GRP: {exc}"
        ) from exc

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            "CSV do GRP inválido. "
            "Colunas ausentes: "
            + ", ".join(sorted(missing))
        )

    records = []

    for index, row in df.iterrows():
        line = index + 2

        supplier = str(row["Fornecedor"]).strip()
        material = str(row["Material"]).strip()

        if (
            not supplier
            or not material
            or supplier.lower() == "nan"
            or material.lower() == "nan"
        ):
            raise ValueError(
                f"Linha {line}: fornecedor/material inválido."
            )

        try:
            capacity = float(row["Capacidade_Semanal"])
            lead_time = int(row["Prazo_Dias"])
            price = float(row["Preco_Unitario"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Linha {line}: dados numéricos inválidos."
            ) from exc

        if capacity < 0 or lead_time < 0 or price < 0:
            raise ValueError(
                f"Linha {line}: capacidade, prazo e preço devem ser >= 0."
            )

        records.append(
            SupplierRecord(
                supplier=supplier,
                material=material,
                capacity=capacity,
                lead_time_days=lead_time,
                unit_price=price,
                status=str(row["Status"]).strip(),
            )
        )

    return records
