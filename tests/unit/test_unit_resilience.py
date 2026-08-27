from pathlib import Path
import pytest
from src.reporting.models import MRPInputContract
from src.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from src.resilience.fallback import JsonMRPProvider, save_mrp_cache


def test_circuit_breaker_transition():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=1)
    assert breaker.state == CircuitState.CLOSED

    # Falha 1
    def _fail():
        raise ValueError("Erro 1")

    with pytest.raises(ValueError):
        breaker.call(_fail)
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 1

    # Falha 2 -> Trip para OPEN
    with pytest.raises(ValueError):
        breaker.call(_fail)
    assert breaker.state == CircuitState.OPEN

    # Chamada subsequente com circuito aberto é bloqueada imediatamente
    with pytest.raises(CircuitOpenError):
        breaker.call(lambda: "ok")


def test_save_and_load_mrp_cache(tmp_path: Path):
    cache_path = tmp_path / "cache_mrp.json"
    items = [
        MRPInputContract("MAT001", "Fornecedor A", 100, 150, 100, 200, 5, "COMPRA_SUGERIDA", ""),
        MRPInputContract("MAT002", "Fornecedor B", 300, 250, 50, 400, 7, "COMPRA_SUGERIDA", ""),
    ]
    save_mrp_cache(items, cache_path)
    assert cache_path.exists()

    provider = JsonMRPProvider(cache_path)
    loaded = provider.get_results()
    assert len(loaded) == 2
    assert loaded[0].material == "MAT001"
    assert loaded[1].material == "MAT002"
