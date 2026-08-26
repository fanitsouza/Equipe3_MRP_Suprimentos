from datetime import date

import pytest

from src.models.data import NFPRecord, StockRecord, SupplierRecord, SupplierUpdate
from src.mrp import DadosInvalidosError, StatusMRP, calcular_mrp_da_coleta


def _coleta_completa() -> dict:
    fornecedores = [
        SupplierRecord("Fornecedor A", "MAT001", 200.0, 5, 100.0, "Ativo"),
        SupplierRecord("Fornecedor C", "MAT003", 150.0, 10, 110.0, "Ativo"),
    ]
    return {
        "stock": [
            StockRecord("MAT001", 100.0, 150.0, 50.0),
            StockRecord("MAT003", 50.0, 180.0, 80.0),
        ],
        "supplier_csv": fornecedores,
        "grp_web": list(fornecedores),
        "nfp": NFPRecord(
            "10452", "Fornecedor A", "MAT001", 180.0, date(2026, 3, 1), 100.0
        ),
        "supplier_update": SupplierUpdate(
            "Fornecedor C", "MAT003", 150.0, 100.0, 10, 14, "Alfândega"
        ),
    }


def test_integra_coleta_com_motor_e_bloqueia_excecao() -> None:
    resultados = calcular_mrp_da_coleta(_coleta_completa())

    por_material = {item.material: item for item in resultados}
    assert por_material["MAT001"].quantidade_sugerida == 100
    assert por_material["MAT003"].quantidade_sugerida is None
    assert (
        por_material["MAT003"].status
        is StatusMRP.AGUARDANDO_VALIDACAO_HUMANA
    )


def test_rejeita_divergencia_entre_csv_e_grp_web() -> None:
    coleta = _coleta_completa()
    coleta["grp_web"][0] = SupplierRecord(
        "Fornecedor A", "MAT001", 199.0, 5, 100.0, "Ativo"
    )

    with pytest.raises(DadosInvalidosError, match="CSV e GRP Web"):
        calcular_mrp_da_coleta(coleta)


def test_rejeita_preco_da_nfp_divergente_do_grp() -> None:
    coleta = _coleta_completa()
    coleta["nfp"] = NFPRecord(
        "10452", "Fornecedor A", "MAT001", 180.0, date(2026, 3, 1), 999.0
    )

    with pytest.raises(DadosInvalidosError, match="Preço da NFP"):
        calcular_mrp_da_coleta(coleta)


def test_rejeita_quantidade_fracionaria_na_integracao() -> None:
    coleta = _coleta_completa()
    coleta["stock"][0] = StockRecord("MAT001", 100.5, 150.0, 50.0)

    with pytest.raises(DadosInvalidosError, match="quantidade inteira"):
        calcular_mrp_da_coleta(coleta)

