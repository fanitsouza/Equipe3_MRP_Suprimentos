from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, TypedDict


class ContractValidationError(ValueError):
    pass


class _MRPInputRequiredDict(TypedDict):
    material: str
    fornecedor: str
    estoque_atual: int
    necessidade: int
    quantidade_comprar: int | None


class MRPInputContractDict(_MRPInputRequiredDict, total=False):
    """Formato esperado pela Responsabilidade 3 apos o adapter do Motor MRP."""

    capacidade: int | None
    prazo_dias: int | None
    status_validacao: str
    observacao: str


@dataclass(frozen=True, slots=True)
class MRPInputContract:
    """Resultado ja calculado pelo Motor MRP para consumo da Responsabilidade 3.

    Esta estrutura e somente um contrato de entrada. Ela nao implementa regras
    de MRP nem deve ser usada para calcular necessidade, estoque, lote ou fornecedor.
    """

    material: str
    fornecedor: str
    estoque_atual: int
    necessidade: int
    quantidade_comprar: int | None
    capacidade: int | None = None
    prazo_dias: int | None = None
    status_validacao: str = "OK"
    observacao: str = ""

    def __post_init__(self) -> None:
        material = _clean_required_text(self.material, "material")
        fornecedor = _clean_required_text(self.fornecedor, "fornecedor")

        object.__setattr__(self, "material", material)
        object.__setattr__(self, "fornecedor", fornecedor)
        object.__setattr__(
            self,
            "estoque_atual",
            _coerce_non_negative_int(self.estoque_atual, "estoque_atual"),
        )
        object.__setattr__(
            self,
            "necessidade",
            _coerce_non_negative_int(self.necessidade, "necessidade"),
        )
        object.__setattr__(
            self,
            "quantidade_comprar",
            _coerce_optional_non_negative_int(
                self.quantidade_comprar, "quantidade_comprar"
            ),
        )
        object.__setattr__(
            self,
            "capacidade",
            _coerce_optional_non_negative_int(self.capacidade, "capacidade"),
        )
        object.__setattr__(
            self,
            "prazo_dias",
            _coerce_optional_non_negative_int(self.prazo_dias, "prazo_dias"),
        )
        object.__setattr__(
            self,
            "status_validacao",
            str(self.status_validacao or "OK").strip(),
        )
        object.__setattr__(self, "observacao", str(self.observacao or "").strip())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_report_row(self) -> dict[str, Any]:
        return {
            "Fornecedor": self.fornecedor,
            "Material": self.material,
            "Estoque": self.estoque_atual,
            "Necessidade": self.necessidade,
            "Capacidade": self.capacidade,
            "Prazo_Dias": self.prazo_dias,
            "Status_Validacao": self.status_validacao,
            "Observacao": self.observacao,
        }


def _clean_required_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ContractValidationError(f"Campo obrigatorio vazio: {field}")
    return text


def _coerce_non_negative_int(value: Any, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ContractValidationError(f"Campo numerico invalido: {field}") from exc

    if number < 0:
        raise ContractValidationError(f"Campo numerico negativo: {field}")
    return number


def _coerce_optional_non_negative_int(value: Any, field: str) -> int | None:
    if value in (None, ""):
        return None
    return _coerce_non_negative_int(value, field)
