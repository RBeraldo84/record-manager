from functools import lru_cache

from databricks import sql
from databricks.sdk.core import Config

from config import get_settings


def get_connection():
    settings = get_settings().databricks
    cfg = _get_config(settings.config_profile)

    server_hostname = cfg.host.replace(
        "https://",
        "",
    ).rstrip("/")

    return sql.connect(
        server_hostname=server_hostname,
        http_path=f"/sql/1.0/warehouses/{settings.warehouse_id}",
        credentials_provider=lambda: cfg.authenticate,
    )


@lru_cache(maxsize=4)
def _get_config(profile: str | None):
    if profile:
        return Config(profile=profile)
    return Config()
