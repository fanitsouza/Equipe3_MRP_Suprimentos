from pathlib import Path
import pytest
from src.collectors.grp_web import collect_grp_web


def test_collect_grp_web_missing_credentials():
    with pytest.raises(ValueError, match="GRP_USER e GRP_PASSWORD precisam estar configurados"):
        collect_grp_web("http://localhost:8000/grp.html", "", "")


def test_collect_grp_web_empty_user():
    with pytest.raises(ValueError):
        collect_grp_web("http://localhost:8000/grp.html", "", "senha")


def test_collect_grp_web_empty_password():
    with pytest.raises(ValueError):
        collect_grp_web("http://localhost:8000/grp.html", "usuario", "")


def test_collect_grp_web_file_url():
    html_path = Path("Source/web/grp_fake.html").resolve()
    if html_path.exists():
        file_url = html_path.as_uri()
        records = collect_grp_web(file_url, "aluno", "avaliacao2026", headless=True)
        assert len(records) >= 4
        assert records[0].supplier == "Fornecedor A"
        assert records[0].material == "MAT001"
