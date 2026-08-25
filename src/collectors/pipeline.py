from src.collectors.email import collect_supplier_email
from src.collectors.grp_csv import collect_supplier_csv
from src.collectors.grp_web import collect_grp_web
from src.collectors.nfp import collect_nfp
from src.collectors.stock import collect_stock
from src.config import Settings
from src.logger import logger


def collect_all(settings: Settings) -> dict:

    source = settings.source_dir

    logger.info("Iniciando processo de coleta de dados.")

    # 1. Estoque
    try:
        stock = collect_stock(
            source / "estoque_producao.xlsx"
        )

        logger.info(
            "coleta_estoque | %d registros processados.",
            len(stock),
        )

    except Exception:
        logger.exception(
            "coleta_estoque | ERRO durante a leitura."
        )
        raise

    # 2. GRP CSV
    try:
        supplier_csv = collect_supplier_csv(
            source / "GRP_fornecedores_capacidade.csv"
        )

        logger.info(
            "coleta_grp_csv | %d registros processados.",
            len(supplier_csv),
        )

    except Exception:
        logger.exception(
            "coleta_grp_csv | ERRO durante a leitura."
        )
        raise

    # 3. GRP Web
    try:
        grp_web = collect_grp_web(
            settings.grp_url,
            settings.grp_user,
            settings.grp_password,
        )

        logger.info(
            "coleta_grp_web | %d registros extraídos.",
            len(grp_web),
        )

    except Exception:
        logger.exception(
            "coleta_grp_web | ERRO durante acesso ao GRP."
        )
        raise

    # 4. NFP
    try:
        nfp = collect_nfp(
            source
            / "NFP"
            / "NFP_10452_fornecedor_A.pdf"
        )

        logger.info(
            "coleta_nfp | NFP %s processada.",
            nfp.number,
        )

    except Exception:
        logger.exception(
            "coleta_nfp | ERRO durante leitura da NFP."
        )
        raise

    # 5. E-mail
    try:
        supplier_update = collect_supplier_email(
            source
            / "emails"
            / "email_atualizacao_fornecedor_C.txt"
        )

        logger.info(
            "coleta_email | atualização de %s/%s identificada.",
            supplier_update.supplier,
            supplier_update.material,
        )

        if (
            supplier_update.old_capacity
            != supplier_update.new_capacity
            or supplier_update.old_lead_time_days
            != supplier_update.new_lead_time_days
        ):
            logger.warning(
                "AVISO | %s/%s possui divergência: "
                "capacidade %.0f -> %.0f; "
                "prazo %d -> %d dias.",
                supplier_update.supplier,
                supplier_update.material,
                supplier_update.old_capacity,
                supplier_update.new_capacity,
                supplier_update.old_lead_time_days,
                supplier_update.new_lead_time_days,
            )

    except Exception:
        logger.exception(
            "coleta_email | ERRO durante leitura do e-mail."
        )
        raise

    logger.info(
        "Coleta de todas as fontes concluída com sucesso."
    )

    return {
        "stock": stock,
        "supplier_csv": supplier_csv,
        "grp_web": grp_web,
        "nfp": nfp,
        "supplier_update": supplier_update,
    }
