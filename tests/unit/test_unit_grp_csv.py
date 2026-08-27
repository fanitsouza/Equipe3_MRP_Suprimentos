from pathlib import Path
import pytest
import pandas as pd
from src.collectors.grp_csv import collect_supplier_csv
from src.models.data import SupplierRecord


def test_collect_supplier_csv_success(tmp_path: Path):
    csv_path = tmp_path / "fornecedores.csv"
    df = pd.DataFrame([
        {
            "Fornecedor": "Fornecedor A",
            "Material": "MAT001",
            "Capacidade_Semanal": 200.0,
            "Prazo_Dias": 5,
            "Preco_Unitario": 100.0,
            "Status": "Ativo",
        },
        {
            "Fornecedor": "Fornecedor B",
            "Material": "MAT002",
            "Capacidade_Semanal": 400.0,
            "Prazo_Dias": 7,
            "Preco_Unitario": 90.0,
            "Status": "Ativo",
        },
    ])
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    records = collect_supplier_csv(csv_path)
    assert len(records) == 2
    assert isinstance(records[0], SupplierRecord)
    assert records[0].supplier == "Fornecedor A"
    assert records[0].material == "MAT001"
    assert records[0].capacity == 200.0
    assert records[0].lead_time_days == 5
    assert records[0].unit_price == 100.0
    assert records[0].status == "Ativo"


def test_collect_supplier_csv_missing_columns(tmp_path: Path):
    csv_path = tmp_path / "fornecedores_invalido.csv"
    df = pd.DataFrame([
        {"Fornecedor": "Fornecedor A", "Material": "MAT001"}
    ])
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    with pytest.raises(ValueError, match="Colunas ausentes"):
        collect_supplier_csv(csv_path)


def test_collect_supplier_csv_nonexistent(tmp_path: Path):
    with pytest.raises(Exception):
        collect_supplier_csv(tmp_path / "nao_existe.csv")
