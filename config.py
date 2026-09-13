import os
import re
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def quote_identifier(identifier: str) -> str:
    if not _IDENTIFIER_RE.match(identifier):
        raise ValueError(
            f"Identificador invalido para Unity Catalog: {identifier!r}"
        )
    return f"`{identifier}`"


def qualified_table_name(catalog: str, schema: str, table: str) -> str:
    return ".".join(
        quote_identifier(part)
        for part in (catalog, schema, table)
    )


@dataclass(frozen=True)
class DatabricksSettings:
    warehouse_id: str
    config_profile: str | None = None


@dataclass(frozen=True)
class TableSettings:
    catalog: str
    schema: str
    records_table: str
    audit_table: str

    @property
    def records_full_name(self) -> str:
        return qualified_table_name(
            self.catalog,
            self.schema,
            self.records_table,
        )

    @property
    def audit_full_name(self) -> str:
        return qualified_table_name(
            self.catalog,
            self.schema,
            self.audit_table,
        )


@dataclass(frozen=True)
class AppSettings:
    databricks: DatabricksSettings
    tables: TableSettings


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    load_dotenv()

    warehouse_id = _optional_env("DATABRICKS_WAREHOUSE_ID")
    if not warehouse_id:
        raise RuntimeError("DATABRICKS_WAREHOUSE_ID nao configurado.")

    tables = TableSettings(
        catalog=os.getenv("TARGET_CATALOG", "raw_db").strip(),
        schema=os.getenv("TARGET_SCHEMA", "default").strip(),
        records_table=os.getenv("TARGET_TABLE", "app_records").strip(),
        audit_table=os.getenv("AUDIT_TABLE", "app_audit").strip(),
    )

    # Validate eagerly so config errors fail before the first SQL execution.
    _ = tables.records_full_name
    _ = tables.audit_full_name

    return AppSettings(
        databricks=DatabricksSettings(
            warehouse_id=warehouse_id,
            config_profile=_optional_env("DATABRICKS_CONFIG_PROFILE"),
        ),
        tables=tables,
    )
