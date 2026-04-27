"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bot_4_shazam"
    db_user: str = "postgres"
    db_password: str = ""

    # юзернейм бота (для подписи)
    bot_username: str = ""

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # URL Bot API (на случай Local Bot API; по умолчанию публичный)
    bot_api_url: str = "https://api.telegram.org"

    # === yt-dlp прокси (для скачивания трека после распознавания) ===
    # Резидентный SOCKS5 прокси (приоритет 1) — например socks5://user:pass@host:port
    proxy_url: str = ""
    # Cloudflare WARP внутри docker-compose (приоритет 2)
    warp_enabled: bool = False

    # максимальный размер входящего файла (МБ)
    max_input_mb: int = 20

    # длина семпла для Shazam (секунды)
    sample_duration: int = 15

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# глобальный экземпляр настроек
settings = Settings()
