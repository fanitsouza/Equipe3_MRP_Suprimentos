from pathlib import Path
import pytest
import pandas as pd
from src.collectors.stock import collect_stock
from src.models.data import StockRecord


def test_collect_stock_success(tmp_path: Path):
    excel_path = tmp_path / "estoque_teste.xlsx"
    df = pd.DataFrame([
        {"Codigo_Material": "MAT001", "Estoque_Atual": 100.0, "Demanda_Semanal": 150.0, "Estoque_Seguranca": 50.0},
        {"Codigo_Material": "MAT002", "Estoque_Atual": 300.0, "Demanda_Semanal": 250.0, "Estoque_Seguranca": 100.0},
    ])
    df.to_excel(excel_path, index=False)

    records = collect_stock(excel_path)
    assert len(records) == 2
    assert isinstance(records[0], StockRecord)
    assert records[0].material == "MAT001"
    assert records[0].stock == 100.0
    assert records[0].weekly_demand == 150.0
    assert records[0].safety_stock == 50.0


def test_collect_stock_missing_columns(tmp_path: Path):
    excel_path = tmp_path / "estoque_invalido.xlsx"
    df = pd.DataFrame([
        {"Codigo_Material": "MAT001", "Estoque_Atual": 100.0}
    ])
    df.to_excel(excel_path, index=False)

    with pytest.raises(ValueError, match="Colunas ausentes"):
        collect_stock(excel_path)


def test_collect_stock_nonexistent_file(tmp_path: Path):
    with pytest.raises(Exception):
        collect_stock(tmp_path / "inexistente.xlsx")
