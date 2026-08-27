from src.mrp.engine import calcular_mrp
from src.mrp.models import AtualizacaoFornecedor, EstoqueMaterial, Fornecedor, StatusMRP, Severidade


def test_regression_cenario_aprovado_sugestao_compra():
    """Cenário Aprovado: Necessidade líquida calculada com fornecedor ativo e capacidade disponível."""
    estoque = EstoqueMaterial("MAT001", estoque_atual=100, demanda_semanal=150, estoque_seguranca=50)
    fornecedor = Fornecedor("Fornecedor A", "MAT001", capacidade_semanal=200, prazo_dias=5, preco_unitario=100.0)

    resultados = calcular_mrp([estoque], [fornecedor])
    assert len(resultados) == 1
    res = resultados[0]

    # Necessidade = Demanda (150) + Seguranca (50) - Estoque (100) = 100
    assert res.necessidade_calculada == 100
    assert res.quantidade_sugerida == 100
    assert res.status == StatusMRP.COMPRA_SUGERIDA
    assert res.severidade == Severidade.INFO
    assert not res.requer_validacao_humana


def test_regression_cenario_excecao_fornecedor_c_humano_no_loop():
    """Cenário de Exceção: Fornecedor C com atraso e redução de capacidade retido para validação humana."""
    estoque = EstoqueMaterial("MAT003", estoque_atual=50, demanda_semanal=180, estoque_seguranca=80)
    fornecedor = Fornecedor("Fornecedor C", "MAT003", capacidade_semanal=150, prazo_dias=10, preco_unitario=110.0)
    atualizacao = AtualizacaoFornecedor("Fornecedor C", "MAT003", capacidade_semanal=100, prazo_dias=14)

    resultados = calcular_mrp([estoque], [fornecedor], [atualizacao])
    assert len(resultados) == 1
    res = resultados[0]

    # Necessidade = 180 + 80 - 50 = 210
    assert res.necessidade_calculada == 210
    assert res.quantidade_sugerida is None  # Não sugere compra automática
    assert res.status == StatusMRP.AGUARDANDO_VALIDACAO_HUMANA
    assert res.severidade == Severidade.AVISO
    assert res.requer_validacao_humana is True
    assert res.capacidade_considerada == 100
    assert res.prazo_considerado_dias == 14


def test_regression_cenario_estoque_excedente_sem_compra():
    """Cenário de Estoque Suficiente: Nenhuma compra sugerida quando estoque >= demanda + segurança."""
    estoque = EstoqueMaterial("MAT002", estoque_atual=400, demanda_semanal=250, estoque_seguranca=100)
    fornecedor = Fornecedor("Fornecedor B", "MAT002", capacidade_semanal=400, prazo_dias=7, preco_unitario=90.0)

    resultados = calcular_mrp([estoque], [fornecedor])
    res = resultados[0]

    assert res.necessidade_calculada == 0
    assert res.quantidade_sugerida == 0
    assert res.status == StatusMRP.SEM_COMPRA
