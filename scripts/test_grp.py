from src.config import get_settings
from src.collectors.grp_web import collect_grp_web


settings = get_settings()

print("Iniciando automação do GRP...")
print(f"URL: {settings.grp_url}")

records = collect_grp_web(
    settings.grp_url,
    settings.grp_user,
    settings.grp_password,
    headless=False
)

print()
print("=== DADOS EXTRAÍDOS DO GRP ===")

for record in records:
    print(
        f"{record.supplier} | "
        f"{record.material} | "
        f"capacidade: {record.capacity} | "
        f"prazo: {record.lead_time_days} dias | "
        f"preço: {record.unit_price}"
    )

print()
print(f"Total de registros: {len(records)}")
