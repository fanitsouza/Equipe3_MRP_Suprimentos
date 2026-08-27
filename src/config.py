import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / "Source" / ".env")


@dataclass(frozen=True)
class Settings:
    source_dir: Path
    output_dir: Path
    alert_file: Path
    grp_url: str
    grp_user: str
    grp_password: str
    timezone: str


def get_settings() -> Settings:
    return Settings(
        source_dir=Path(
            os.getenv("SOURCE_DIR", str(ROOT_DIR / "Source"))
        ).resolve(),
        output_dir=Path(
            os.getenv("OUTPUT_DIR", str(ROOT_DIR / "output"))
        ).resolve(),
        alert_file=Path(
            os.getenv("ALERT_FILE", str(ROOT_DIR / "logs" / "alerts.jsonl"))
        ).resolve(),
        grp_url=os.getenv(
            "GRP_URL",
            "http://localhost:8000/web/grp_fake.html"
        ),
        grp_user=os.getenv("GRP_USER", ""),
        grp_password=os.getenv("GRP_PASSWORD", ""),
        timezone=os.getenv("TZ", "America/Manaus"),
    )
