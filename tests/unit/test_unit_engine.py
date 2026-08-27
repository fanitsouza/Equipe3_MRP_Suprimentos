from src.mrp.engine import calcular_mrp
from src.mrp.models import (
    AtualizacaoFornecedor,
    EstoqueMaterial,
    Fornecedor,
    Severidade,
    StatusMRP,
)


def test_calcular_mrp_compra_normal():
    estoques = [EstoqueMaterial("MAT001", estoque_atual=100, demanda_semanal=150, estoque_seguranca=50)]
    fornecedores = [Fornecedor("Fornecedor A", "MAT001", capacidade_semanal=200, prazo_dias=5, preco_unitario=100.0)]

    resultados = calcular_mrp(estoques, fornecedores)
    assert len(resultados) == 1
    res = resultados[0]
    assert res.material == "MAT001"
    assert res.necessidade_calculada == 100
    assert res.quantidade_sugerida == 100
    assert res.status == StatusMRP.COMPRA_SUGERIDA
    assert res.severidade == Severidade.INFO
    assert not res.requer_validacao_humana


def test_calcular_mrp_sem_necessidade_compra():
    estoques = [EstoqueMaterial("MAT002", estoque_atual=300, demanda_semanal=200, estoque_seguranca=50)]
    fornecedores = [Fornecedor("Fornecedor B", "MAT002", capacidade_semanal=400, prazo_dias=7, preco_unitario=90.0)]

    resultados = calcular_mrp(estoques, fornecedores)
    res = resultados[0]
    assert res.necessidade_calculada == 0
    assert res.quantidade_sugerida == 0
    assert res.status == StatusMRP.SEM_COMPRA


def test_calcular_mrp_capacidade_insuficiente():
    estoques = [EstoqueMaterial("MAT004", estoque_atual=50, demanda_semanal=400, estoque_seguranca=50)]
    fornecedores = [Fornecedor("Fornecedor D", "MAT004", capacidade_semanal=200, prazo_dias=6, preco_unitario=105.0)]

    resultados = calcular_mrp(estoques, fornecedores)
    res = resultados[0]
    assert res.necessidade_calculada == 400
    assert res.quantidade_sugerida == 400
    assert res.status == StatusMRP.CAPACIDADE_INSUFICIENTE


def test_calcular_mrp_com_atualizacao_divergente_fornecedor_c():
    estoques = [EstoqueMaterial("MAT003", estoque_atual=50, demanda_semanal=180, estoque_seguranca=80)]
    fornecedores = [Fornecedor("Fornecedor C", "MAT003", capacidade_semanal=150, prazo_dias=10, preco_unitario=110.0)]
    atualizacoes = [AtualizacaoFornecedor("Fornecedor C", "MAT003", capacidade_semanal=100, prazo_dias=14)]

    resultados = calcular_mrp(estoques, fornecedores, atualizacoes)
    res = resultados[0]
    assert res.necessidade_calculada == 210
    assert res.quantidade_sugerida is None
    assert res.status == StatusMRP.AGUARDANDO_VALIDACAO_HUMANA
    assert res.severidade == Severidade.AVISO
    assert res.requer_validacao_humana is True
