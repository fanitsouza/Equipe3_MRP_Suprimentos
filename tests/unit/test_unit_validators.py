import pytest
from src.mrp.exceptions import DadosInvalidosError
from src.mrp.models import AtualizacaoFornecedor, EstoqueMaterial, Fornecedor
from src.mrp.validators import validar_atualizacoes, validar_estoques, validar_fornecedores


def test_validar_estoques_ok():
    estoques = [EstoqueMaterial("MAT001", 100, 150, 50)]
    validados = validar_estoques(estoques)
    assert len(validados) == 1


def test_validar_estoques_negativos():
    with pytest.raises(DadosInvalidosError, match="estoque_atual inválido"):
        validar_estoques([EstoqueMaterial("MAT001", -10, 150, 50)])


def test_validar_estoques_vazios():
    with pytest.raises(DadosInvalidosError, match="não pode estar vazia"):
        validar_estoques([])


def test_validar_fornecedores_ok():
    fornecedores = [Fornecedor("Fornecedor A", "MAT001", 200, 5, 100.0)]
    validados = validar_fornecedores(fornecedores)
    assert len(validados) == 1


def test_validar_fornecedores_capacidade_negativa():
    with pytest.raises(DadosInvalidosError, match="capacidade_semanal inválido"):
        validar_fornecedores([Fornecedor("Fornecedor A", "MAT001", -5, 5, 100.0)])


def test_validar_fornecedores_duplicados():
    with pytest.raises(DadosInvalidosError, match="Mais de um fornecedor principal"):
        validar_fornecedores([
            Fornecedor("Fornecedor A", "MAT001", 200, 5, 100.0),
            Fornecedor("Fornecedor B", "MAT001", 300, 7, 90.0),
        ])


def test_validar_atualizacoes_ok():
    atualizacoes = [AtualizacaoFornecedor("Fornecedor C", "MAT003", 100, 14)]
    validados = validar_atualizacoes(atualizacoes)
    assert len(validados) == 1
