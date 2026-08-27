from pathlib import Path
import pytest
from src.collectors.email import collect_supplier_email
from src.models.data import SupplierUpdate


def test_collect_supplier_email_success(tmp_path: Path):
    email_path = tmp_path / "email.txt"
    email_path.write_text(
        "De: compras@fornecedor-c.example\n"
        "Para: suprimentos@portalfake.example\n"
        "Assunto: Atualização de capacidade e prazo — MAT003\n\n"
        "Por problemas de alfândega, a capacidade semanal do MAT003 foi reduzida de 150 para 100 unidades.\n"
        "O prazo de entrega passou de 10 para 14 dias.\n\n"
        "Fornecedor C\n",
        encoding="utf-8",
    )

    update = collect_supplier_email(email_path)
    assert isinstance(update, SupplierUpdate)
    assert update.supplier == "Fornecedor C"
    assert update.material == "MAT003"
    assert update.old_capacity == 150.0
    assert update.new_capacity == 100.0
    assert update.old_lead_time_days == 10
    assert update.new_lead_time_days == 14
    assert "alfândega" in update.reason.lower()


def test_collect_supplier_email_invalid_format(tmp_path: Path):
    email_path = tmp_path / "email_invalido.txt"
    email_path.write_text("Mensagem vazia sem padrao.\n", encoding="utf-8")

    with pytest.raises(ValueError, match="não identificados"):
        collect_supplier_email(email_path)
