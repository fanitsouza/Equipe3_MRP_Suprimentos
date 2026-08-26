from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.models.data import SupplierRecord


def collect_grp_web(
    url: str,
    username: str,
    password: str,
    headless: bool = True,
    timeout_ms: int = 10000,
) -> list[SupplierRecord]:

    if not username or not password:
        raise ValueError(
            "GRP_USER e GRP_PASSWORD precisam estar configurados."
        )

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=headless
        )

        page = browser.new_page()

        page.set_default_timeout(timeout_ms)

        try:
            page.goto(
                url,
                wait_until="domcontentloaded"
            )

            page.locator("#u").fill(username)
            page.locator("#p").fill(password)

            page.get_by_role(
                "button",
                name="Entrar"
            ).click()

            page.locator("#app").wait_for(
                state="visible"
            )

            rows = page.locator(
                "#app table tr"
            )

            count = rows.count()

            if count <= 1:
                raise ValueError(
                    "GRP acessado, mas nenhuma linha "
                    "de fornecedor foi encontrada."
                )

            records = []

            for index in range(1, count):

                cells = rows.nth(index).locator("td")

                values = [
                    cells.nth(column).inner_text().strip()
                    for column in range(cells.count())
                ]

                if len(values) != 5:
                    raise ValueError(
                        f"Linha {index + 1} do GRP possui "
                        f"formato inesperado: {values}"
                    )

                (
                    supplier,
                    material,
                    capacity_raw,
                    lead_time_raw,
                    price_raw,
                ) = values

                try:
                    capacity = float(capacity_raw)
                    lead_time = int(lead_time_raw)
                    price = float(price_raw)

                except ValueError as exc:
                    raise ValueError(
                        f"Dados numéricos inválidos no GRP "
                        f"para {supplier}/{material}"
                    ) from exc

                records.append(
                    SupplierRecord(
                        supplier=supplier,
                        material=material,
                        capacity=capacity,
                        lead_time_days=lead_time,
                        unit_price=price,
                        status="Ativo",
                    )
                )

            return records

        except PlaywrightTimeoutError as exc:
            raise RuntimeError(
                f"Timeout ao acessar ou extrair o GRP: {url}"
            ) from exc

        finally:
            browser.close()
