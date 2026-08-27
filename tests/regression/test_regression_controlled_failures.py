from pathlib import Path
import pytest
from src.collectors.grp_web import collect_grp_web
from src.collectors.stock import collect_stock
from src.mrp.engine import calcular_mrp
from src.mrp.exceptions import DadosInvalidosError
from src.mrp.models import EstoqueMaterial, Fornecedor
from src.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError


def test_regression_falha_controlada_estoque_negativo():
    """Falha controlada 1: Rejeição estrita de estoque negativo."""
    estoque = EstoqueMaterial("MAT001", estoque_atual=-50, demanda_semanal=150, estoque_seguranca=50)
    fornecedor = Fornecedor("Fornecedor A", "MAT001", capacidade_semanal=200, prazo_dias=5, preco_unitario=100.0)

    with pytest.raises(DadosInvalidosError, match="estoque_atual inválido"):
        calcular_mrp([estoque], [fornecedor])


def test_regression_falha_controlada_demanda_negativa():
    """Falha controlada 2: Rejeição de demanda negativa."""
    estoque = EstoqueMaterial("MAT001", estoque_atual=100, demanda_semanal=-20, estoque_seguranca=50)
    fornecedor = Fornecedor("Fornecedor A", "MAT001", capacidade_semanal=200, prazo_dias=5, preco_unitario=100.0)

    with pytest.raises(DadosInvalidosError, match="demanda_semanal inválido"):
        calcular_mrp([estoque], [fornecedor])


def test_regression_falha_controlada_fornecedor_ausente():
    """Falha controlada 3: Rejeição de material sem fornecedor homologado."""
    estoque = EstoqueMaterial("MAT999", estoque_atual=100, demanda_semanal=150, estoque_seguranca=50)
    fornecedor = Fornecedor("Fornecedor A", "MAT001", capacidade_semanal=200, prazo_dias=5, preco_unitario=100.0)

    with pytest.raises(DadosInvalidosError, match="Fornecedor não encontrado"):
        calcular_mrp([estoque], [fornecedor])


def test_regression_falha_controlada_credenciais_vazias_grp():
    """Falha controlada 4: Bloqueio de acesso web ao GRP sem credenciais informadas."""
    with pytest.raises(ValueError, match="GRP_USER e GRP_PASSWORD"):
        collect_grp_web("http://localhost:8000/grp.html", "", "")


def test_regression_falha_controlada_arquivo_inexistente(tmp_path: Path):
    """Falha controlada 5: Tratamento de exceção para arquivo de entrada inexistente."""
    with pytest.raises(Exception):
        collect_stock(tmp_path / "arquivo_nao_encontrado.xlsx")


def test_regression_falha_controlada_circuit_breaker_bloqueio():
    """Falha controlada 6: Bloqueio preventivo de chamadas pelo Circuit Breaker após 3 falhas."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)

    def _fail():
        raise ConnectionError("Falha na conexao")

    for _ in range(3):
        try:
            breaker.call(_fail)
        except ConnectionError:
            pass

    # A 4ª tentativa deve ser bloqueada imediatamente pelo CircuitOpenError
    with pytest.raises(CircuitOpenError):
        breaker.call(lambda: "ok")
