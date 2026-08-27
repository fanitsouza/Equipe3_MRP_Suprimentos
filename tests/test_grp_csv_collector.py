from pathlib import Path

from src.collectors.grp_csv import collect_supplier_csv


def test_collect_supplier_csv():

    records = collect_supplier_csv(
        Path("Source/GRP_fornecedores_capacidade.csv")
    )

    assert len(records) == 4

    assert records[2].supplier == "Fornecedor C"
    assert records[2].material == "MAT003"
    assert records[2].capacity == 150
    assert records[2].lead_time_days == 10
