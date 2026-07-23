from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "APEC Digital Platform"
    database_url: str = "sqlite:///./apec.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24
    # Каталог со старыми JSON-выгрузками (schedule.json, groups.json, teachers.json)
    legacy_data_dir: Path = Path(__file__).resolve().parents[4] / "docs" / "api"
    auto_import_legacy: bool = True

    class Config:
        env_prefix = "APEC_"
        env_file = ".env"


settings = Settings()
