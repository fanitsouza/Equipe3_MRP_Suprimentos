import json
import logging
from pathlib import Path
from src.observability.alerts import InMemoryAlertSink, JsonLinesAlertSink, send_alert
from src.observability.severity import Severity
from src.observability.structured_logging import log_event


def test_log_event_structured():
    logger = logging.getLogger("test_logger")
    log_event(
        logger,
        Severity.INFO,
        event="teste_evento",
        module="test_module",
        message="Mensagem de teste",
        execution_id="exec-123",
        context={"chave": "valor"},
    )


def test_in_memory_alert_sink():
    sink = InMemoryAlertSink()
    send_alert(
        sink,
        Severity.AVISO,
        "Alerta de aviso de teste",
        context={"item": "MAT003"},
        code="AVISO_TESTE",
        execution_id="exec-456",
    )
    assert len(sink.alerts) == 1
    alert = sink.alerts[0]
    assert alert.level == "AVISO"
    assert alert.message == "Alerta de aviso de teste"
    assert alert.context["item"] == "MAT003"


def test_json_lines_alert_sink(tmp_path: Path):
    alert_file = tmp_path / "alerts.jsonl"
    sink = JsonLinesAlertSink(alert_file)
    send_alert(
        sink,
        Severity.CRITICO,
        "Falha crítica",
        code="FALHA_CRITICA",
        execution_id="exec-789",
    )
    assert alert_file.exists()
    lines = alert_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["level"] == "CRÍTICO"
    assert data["code"] == "FALHA_CRITICA"
