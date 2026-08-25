import pytest

from src.mrp import (
    AtualizacaoFornecedor,
    DadosInvalidosError,
    EstoqueMaterial,
    Fornecedor,
    Severidade,
    StatusMRP,
    calcular_mrp,
)


def _fornecedor(material: str = "MAT001", capacidade: int = 200) -> Fornecedor:
    return Fornecedor("Fornecedor A", material, capacidade, 5, 100.0)


def test_calcula_necessidade_liquida_e_sugere_compra() -> None:
    resultados = calcular_mrp(
        [EstoqueMaterial("MAT001", 100, 150, 50)],
        [_fornecedor()],
    )

    resultado = resultados[0]
    assert resultado.necessidade_calculada == 100
    assert resultado.quantidade_sugerida == 100
    assert resultado.status is StatusMRP.COMPRA_SUGERIDA
    assert resultado.severidade is Severidade.INFO


def test_nao_sugere_compra_quando_estoque_e_suficiente() -> None:
    resultado = calcular_mrp(
        [EstoqueMaterial("MAT001", 300, 150, 50)],
        [_fornecedor()],
    )[0]

    assert resultado.necessidade_calculada == 0
    assert resultado.quantidade_sugerida == 0
    assert resultado.status is StatusMRP.SEM_COMPRA


def test_indica_capacidade_insuficiente() -> None:
    resultado = calcular_mrp(
        [EstoqueMaterial("MAT001", 0, 250, 50)],
        [_fornecedor(capacidade=200)],
    )[0]

    assert resultado.quantidade_sugerida == 300
    assert resultado.status is StatusMRP.CAPACIDADE_INSUFICIENTE


def test_bloqueia_fornecedor_c_com_divergencia_para_validacao_humana() -> None:
    resultado = calcular_mrp(
        [EstoqueMaterial("MAT003", 50, 180, 80)],
        [Fornecedor("Fornecedor C", "MAT003", 150, 10, 110.0)],
        [AtualizacaoFornecedor("Fornecedor C", "MAT003", 100, 14)],
    )[0]

    assert resultado.necessidade_calculada == 210
    assert resultado.quantidade_sugerida is None
    assert resultado.capacidade_considerada == 100
    assert resultado.prazo_considerado_dias == 14
    assert resultado.status is StatusMRP.AGUARDANDO_VALIDACAO_HUMANA
    assert resultado.severidade is Severidade.AVISO
    assert resultado.requer_validacao_humana is True


@pytest.mark.parametrize(
    "estoque",
    [
        EstoqueMaterial("MAT001", -1, 150, 50),
        EstoqueMaterial("MAT001", 100, -1, 50),
        EstoqueMaterial("MAT001", 100, 150, -1),
    ],
)
def test_rejeita_valores_negativos(estoque: EstoqueMaterial) -> None:
    with pytest.raises(DadosInvalidosError):
        calcular_mrp([estoque], [_fornecedor()])


def test_rejeita_material_sem_fornecedor() -> None:
    with pytest.raises(DadosInvalidosError, match="Fornecedor não encontrado"):
        calcular_mrp(
            [EstoqueMaterial("MAT999", 10, 20, 5)],
            [_fornecedor()],
        )

