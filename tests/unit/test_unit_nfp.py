from pathlib import Path
from datetime import date
import pytest
from src.collectors.nfp import collect_nfp
from src.models.data import NFPRecord


def test_collect_nfp_real_source():
    real_pdf = Path("Source/NFP/NFP_10452_fornecedor_A.pdf")
    if real_pdf.exists():
        record = collect_nfp(real_pdf)
        assert isinstance(record, NFPRecord)
        assert record.number == "10452"
        assert record.supplier == "Fornecedor A"
        assert record.material == "MAT001"
        assert record.quantity == 180.0
        assert record.unit_price == 100.0
        assert isinstance(record.issue_date, date)


def test_collect_nfp_nonexistent_file(tmp_path: Path):
    with pytest.raises(Exception):
        collect_nfp(tmp_path / "nfp_fantasma.pdf")
