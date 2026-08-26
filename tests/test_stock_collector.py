from pathlib import Path

from src.collectors.stock import collect_stock


def test_collect_stock():
    records = collect_stock(
        Path("Source/estoque_producao.xlsx")
    )

    assert len(records) == 4
    assert records[0].material == "MAT001"
    assert records[0].stock == 100
    assert records[0].weekly_demand == 150
    assert records[0].safety_stock == 50
