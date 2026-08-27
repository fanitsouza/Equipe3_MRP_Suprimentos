from pathlib import Path
from src.collectors.pipeline import collect_all
from src.config import Settings
from src.models.data import NFPRecord, SupplierUpdate


def test_collect_all_integrated(tmp_path: Path):
    source_dir = Path("Source").resolve()
    settings = Settings(
        source_dir=source_dir,
        output_dir=tmp_path / "output",
        alert_file=tmp_path / "logs" / "alerts.jsonl",
        grp_url=(source_dir / "web" / "grp_fake.html").as_uri(),
        grp_user="aluno",
        grp_password="avaliacao2026",
        timezone="America/Manaus",
    )

    result = collect_all(settings)

    assert "stock" in result
    assert "supplier_csv" in result
    assert "grp_web" in result
    assert "nfp" in result
    assert "supplier_update" in result

    assert len(result["stock"]) >= 4
    assert len(result["supplier_csv"]) >= 4
    assert len(result["grp_web"]) >= 4
    assert isinstance(result["nfp"], NFPRecord)
    assert isinstance(result["supplier_update"], SupplierUpdate)
