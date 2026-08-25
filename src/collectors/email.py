import re
from pathlib import Path

from src.models.data import SupplierUpdate


def extract_number(
    pattern: str,
    text: str,
    field: str,
    integer: bool = False,
):

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    if not match:
        raise ValueError(
            f"Não foi possível identificar {field} no e-mail."
        )

    value = float(match.group(1))

    return int(value) if integer else value


def collect_supplier_email(path: Path) -> SupplierUpdate:

    if not path.exists():
        raise FileNotFoundError(
            f"E-mail simulado não encontrado: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    supplier_match = re.search(
        r"Fornecedor\s+([A-Z])\s*$",
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    material_match = re.search(
        r"MAT\d+",
        text,
        flags=re.IGNORECASE
    )

    if not supplier_match or not material_match:
        raise ValueError(
            "E-mail inválido: fornecedor/material "
            "não identificados."
        )

    supplier = (
        f"Fornecedor "
        f"{supplier_match.group(1).upper()}"
    )

    material = material_match.group(0).upper()

    old_capacity = extract_number(
        r"capacidade semanal do MAT\d+ "
        r"foi reduzida de "
        r"(\d+(?:[.,]\d+)?)",
        text,
        "capacidade anterior"
    )

    new_capacity = extract_number(
        r"reduzida de "
        r"\d+(?:[.,]\d+)? "
        r"para "
        r"(\d+(?:[.,]\d+)?)",
        text,
        "nova capacidade"
    )

    old_lead = extract_number(
        r"prazo de entrega passou de "
        r"(\d+) "
        r"para",
        text,
        "prazo anterior",
        integer=True
    )

    new_lead = extract_number(
        r"prazo de entrega passou de "
        r"\d+ "
        r"para "
        r"(\d+) "
        r"dias",
        text,
        "novo prazo",
        integer=True
    )

    reason = "Atualização informada pelo fornecedor."

    if "alfândega" in text.lower():
        reason = "Problemas de alfândega."

    return SupplierUpdate(
        supplier=supplier,
        material=material,
        old_capacity=old_capacity,
        new_capacity=new_capacity,
        old_lead_time_days=old_lead,
        new_lead_time_days=new_lead,
        reason=reason,
    )
