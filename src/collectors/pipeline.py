from src.collectors.email import collect_supplier_email
from src.collectors.grp_csv import collect_supplier_csv
from src.collectors.grp_web import collect_grp_web
from src.collectors.nfp import collect_nfp
from src.collectors.stock import collect_stock
from src.config import Settings


def collect_all(settings: Settings) -> dict:

    source = settings.source_dir

    stock = collect_stock(
        source / "estoque_producao.xlsx"
    )

    supplier_csv = collect_supplier_csv(
        source / "GRP_fornecedores_capacidade.csv"
    )

    grp_web = collect_grp_web(
        settings.grp_url,
        settings.grp_user,
        settings.grp_password
    )

    nfp = collect_nfp(
        source / "NFP" / "NFP_10452_fornecedor_A.pdf"
    )

    supplier_update = collect_supplier_email(
        source
        / "emails"
        / "email_atualizacao_fornecedor_C.txt"
    )

    return {
        "stock": stock,
        "supplier_csv": supplier_csv,
        "grp_web": grp_web,
        "nfp": nfp,
        "supplier_update": supplier_update,
    }
