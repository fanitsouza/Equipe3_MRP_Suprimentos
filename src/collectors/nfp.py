import re
from datetime import date
from pathlib import Path

from pypdf import PdfReader

from src.models.data import NFPRecord


def extract_field(text: str, field: str) -> str:

    pattern = (
        rf"{re.escape(field)}\s*\n?\s*([^\n]+)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    if not match:
        raise ValueError(
            f"Campo obrigatório ausente na NFP: {field}"
        )

    return match.group(1).strip()


def collect_nfp(path: Path) -> NFPRecord:

    if not path.exists():
        raise FileNotFoundError(
            f"NFP não encontrada: {path}"
        )

    try:
        reader = PdfReader(str(path))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    except Exception as exc:
        raise ValueError(
            f"Não foi possível ler a NFP: {exc}"
        ) from exc

    number = extract_field(text, "Numero_NFP")

    # O PDF pode representar o fornecedor como:
    # "Fornecedor A"
    # ou quebrar o conteúdo em linhas/elementos.
    supplier_match = re.search(
        r"Fornecedor\s*(?:\n|\r\n|\s)+"
        r"(Fornecedor\s+[A-Z]|[A-Z])",
        text,
        flags=re.IGNORECASE
    )

    if not supplier_match:
        raise ValueError(
            "Campo obrigatório ausente na NFP: Fornecedor"
        )

    supplier_value = supplier_match.group(1).strip()

    if re.fullmatch(
        r"[A-Z]",
        supplier_value,
        flags=re.IGNORECASE
    ):
        supplier = f"Fornecedor {supplier_value.upper()}"
    else:
        supplier = supplier_value

    material = extract_field(text, "Material")
    quantity_raw = extract_field(text, "Quantidade")
    date_raw = extract_field(text, "Data_Emissao")
    price_raw = extract_field(text, "Preco_Unitario")

    try:
        quantity = float(
            quantity_raw.replace(",", ".")
        )

        unit_price = float(
            price_raw.replace(",", ".")
        )

        issue_date = date.fromisoformat(date_raw)

    except ValueError as exc:
        raise ValueError(
            "NFP contém valor numérico ou data inválidos."
        ) from exc

    if quantity < 0 or unit_price < 0:
        raise ValueError(
            "NFP não pode possuir quantidade/preço negativos."
        )

    return NFPRecord(
        number=number,
        supplier=supplier,
        material=material,
        quantity=quantity,
        issue_date=issue_date,
        unit_price=unit_price,
    )
