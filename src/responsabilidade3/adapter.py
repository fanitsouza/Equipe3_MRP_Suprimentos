from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .input_contract import ContractValidationError
from .models import MRPResult


class AdapterError(ValueError):
    pass


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "material": (
        "material",
        "produto",
        "codigo_material",
        "codigo_produto",
        "item",
    ),
    "fornecedor": ("fornecedor", "supplier"),
    "estoque_atual": ("estoque_atual", "estoque", "onhand", "on_hand"),
    "necessidade": (
        "necessidade",
        "necessidade_calculada",
        "necessidade_liquida",
        "demanda_mrp",
    ),
    "quantidade_comprar": (
        "quantidade_comprar",
        "qtd_comprar",
        "compra_sugerida",
        "quantidade_sugerida",
    ),
    "capacidade": ("capacidade", "capacidade_semanal"),
    "prazo_dias": ("prazo_dias", "lead_time_dias", "prazo"),
    "status_validacao": ("status_validacao", "status"),
    "observacao": ("observacao", "observacoes", "mensagem"),
}

REQUIRED_FIELDS = (
    "material",
    "fornecedor",
    "estoque_atual",
    "necessidade",
    "quantidade_comprar",
)


def adapt_mrp_records(records: Iterable[Mapping[str, Any]]) -> list[MRPResult]:
    """Converte a saida da Responsabilidade 2 para o contrato da Responsabilidade 3.

    Este adapter apenas renomeia e valida campos. Ele nao calcula necessidade,
    estoque projetado, lote de compra, fornecedor ou qualquer regra especial.
    """

    return [_adapt_one(record, index) for index, record in enumerate(records, start=1)]


def _adapt_one(record: Mapping[str, Any], index: int) -> MRPResult:
    normalized = {_normalize_key(key): value for key, value in record.items()}
    payload: dict[str, Any] = {}

    for target, aliases in FIELD_ALIASES.items():
        value = _first_present(normalized, aliases)
        if value is not None:
            payload[target] = value

    # Compatibilidade com a planilha atual, que possui "Necessidade" mas ainda
    # nao possui coluna separada para "Quantidade Comprar".
    if "quantidade_comprar" not in payload and "necessidade" in payload:
        payload["quantidade_comprar"] = payload["necessidade"]
    if "necessidade" not in payload and "quantidade_comprar" in payload:
        payload["necessidade"] = payload["quantidade_comprar"]

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise AdapterError(
            f"Registro MRP {index} sem campos obrigatorios: {', '.join(missing)}"
        )

    try:
        return MRPResult(
            material=payload["material"],
            fornecedor=payload["fornecedor"],
            estoque_atual=payload["estoque_atual"],
            necessidade=payload["necessidade"],
            quantidade_comprar=payload["quantidade_comprar"],
            capacidade=payload.get("capacidade"),
            prazo_dias=payload.get("prazo_dias"),
            status_validacao=str(payload.get("status_validacao") or "OK").strip(),
            observacao=str(payload.get("observacao") or "").strip(),
        )
    except ContractValidationError as exc:
        raise AdapterError(f"Registro MRP {index} invalido: {exc}") from exc


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_")


def _first_present(normalized: Mapping[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        if alias in normalized and normalized[alias] is not None:
            return normalized[alias]
    return None
