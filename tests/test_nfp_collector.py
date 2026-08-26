from pathlib import Path

from src.collectors.nfp import collect_nfp


def test_collect_nfp():

    nfp = collect_nfp(
        Path(
            "Source/NFP/"
            "NFP_10452_fornecedor_A.pdf"
        )
    )

    assert nfp.number == "10452"
    assert nfp.supplier == "Fornecedor A"
    assert nfp.material == "MAT001"
    assert nfp.quantity == 180
    assert nfp.unit_price == 100
