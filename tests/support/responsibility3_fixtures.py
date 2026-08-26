from __future__ import annotations

from typing import Any

from src.reporting.models import MRPInputContract as MRPResult


def mock_mrp_results() -> list[MRPResult]:
    """Dados ficticios para desenvolver/testar a Responsabilidade 3 isoladamente."""

    return [
        MRPResult(
            material="Parafuso",
            fornecedor="Fornecedor A",
            estoque_atual=100,
            necessidade=250,
            quantidade_comprar=150,
            capacidade=500,
            prazo_dias=5,
            status_validacao="APROVADO",
            observacao="",
        ),
        MRPResult(
            material="Chapa de aco",
            fornecedor="Fornecedor B",
            estoque_atual=20,
            necessidade=100,
            quantidade_comprar=80,
            capacidade=200,
            prazo_dias=10,
            status_validacao="ALERTA",
            observacao="Estoque baixo",
        ),
        MRPResult(
            material="MAT003",
            fornecedor="Fornecedor C",
            estoque_atual=50,
            necessidade=130,
            quantidade_comprar=130,
            capacidade=150,
            prazo_dias=10,
            status_validacao="ATENCAO",
            observacao="Dado externo ficticio; sem regra especial nesta camada",
        ),
    ]


def mock_mrp_raw_records() -> list[dict[str, Any]]:
    return [
        {
            "produto": "MAT001",
            "fornecedor": "Fornecedor A",
            "estoque_atual": 100,
            "necessidade": 50,
            "quantidade_comprar": 50,
            "capacidade": 200,
            "prazo_dias": 5,
            "status_validacao": "OK",
        },
        {
            "Material": "MAT003",
            "Fornecedor": "Fornecedor C",
            "Estoque": 50,
            "Necessidade": 130,
            "Capacidade": 150,
            "Prazo_Dias": 10,
            "Status_Validacao": "ATENCAO",
            "Observacao": "Formato igual ao relatorio atual",
        },
    ]


def mock_invalid_mrp_records() -> list[dict[str, Any]]:
    return [{"material": "MAT999", "fornecedor": "Fornecedor Teste"}]


class FailingMRPProvider:
    def get_results(self) -> list[MRPResult]:
        raise RuntimeError("Motor MRP indisponivel")
