from pprint import pprint

from src.collectors.pipeline import collect_all
from src.config import get_settings


settings = get_settings()

print("========================================")
print("       INICIANDO COLETA COMPLETA")
print("========================================")

result = collect_all(settings)

print("\n=== ESTOQUE / PRODUÇÃO ===")
pprint(result["stock"])

print("\n=== GRP CSV ===")
pprint(result["supplier_csv"])

print("\n=== GRP WEB ===")
pprint(result["grp_web"])

print("\n=== NFP ===")
pprint(result["nfp"])

print("\n=== ATUALIZAÇÃO DO FORNECEDOR ===")
pprint(result["supplier_update"])

print("\n========================================")
print("       COLETA CONCLUÍDA COM SUCESSO")
print("========================================")
