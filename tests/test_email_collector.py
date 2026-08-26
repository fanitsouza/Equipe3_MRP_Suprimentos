from pathlib import Path

from src.collectors.email import collect_supplier_email


def test_supplier_email_exception():

    update = collect_supplier_email(
        Path(
            "Source/emails/"
            "email_atualizacao_fornecedor_C.txt"
        )
    )

    assert update.supplier == "Fornecedor C"
    assert update.material == "MAT003"

    assert update.old_capacity == 150
    assert update.new_capacity == 100

    assert update.old_lead_time_days == 10
    assert update.new_lead_time_days == 14
