from pathlib import Path
from src.config import Settings
from src.pipeline import executar_processo
from src.resilience import CircuitBreaker


def test_circuit_breaker_and_fallback_integration(tmp_path: Path, monkeypatch):
    source_dir = Path("Source").resolve()
    output_dir = tmp_path / "output"
    alert_file = tmp_path / "logs" / "alerts.jsonl"

    settings = Settings(
        source_dir=source_dir,
        output_dir=output_dir,
        alert_file=alert_file,
        grp_url=(source_dir / "web" / "grp_fake.html").as_uri(),
        grp_user="aluno",
        grp_password="avaliacao2026",
        timezone="America/Manaus",
    )

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)

    # 1. Primeira execucao normal (alimenta o cache)
    exec1 = executar_processo(settings, circuit_breaker=breaker)
    assert not exec1.usou_fallback

    # 2. Simular falha critica nas fontes de coleta
    def _falha_coleta(s):
        raise ConnectionError("GRP Web e Fontes indisponiveis simuladas")

    monkeypatch.setattr("src.pipeline.collect_all", _falha_coleta)

    # 3. Executar novamente: deve ativar Fallback via Cache sem crashar
    exec2 = executar_processo(settings, circuit_breaker=breaker)
    assert exec2.usou_fallback
    assert len(exec2.resultados) == len(exec1.resultados)

    # 4. Validar registro de alerta de ativacao de fallback
    alerts = alert_file.read_text(encoding="utf-8")
    assert "MRP_FALLBACK_ATIVADO" in alerts
