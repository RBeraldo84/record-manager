from dataclasses import dataclass
from uuid import uuid4

from config import quote_identifier
from services.database import get_connection


@dataclass(frozen=True)
class AuditRepository:
    audit_table: str
    target_catalog: str
    target_schema: str
    target_table: str

    def create_event(
        self,
        record_id: str,
        action: str,
        user: str,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                columns = self._resolve_columns(cursor)
                insert_columns = [
                    columns["audit_id"],
                    columns["target_catalog"],
                    columns["target_schema"],
                    columns["target_table"],
                    columns["record_id"],
                    columns["action"],
                    columns["old_value"],
                    columns["new_value"],
                    columns["performed_at"],
                    columns["performed_by"],
                ]
                cursor.execute(
                    f"""
                    INSERT INTO {self.audit_table}
                    (
                        {", ".join(insert_columns)}
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, current_timestamp(), ?)
                    """,
                    (
                        str(uuid4()),
                        self.target_catalog,
                        self.target_schema,
                        self.target_table,
                        record_id,
                        action,
                        old_value,
                        new_value,
                        user,
                    ),
                )
            if hasattr(connection, "commit"):
                connection.commit()

    def _resolve_columns(self, cursor) -> dict[str, str]:
        cursor.execute(f"DESCRIBE TABLE {self.audit_table}")
        audit_columns = {
            str(row[0]).strip().lower()
            for row in cursor.fetchall()
            if row and row[0] and not str(row[0]).startswith("#")
        }

        aliases = {
            "audit_id": ("audit_id", "id", "event_id"),
            "target_catalog": ("target_catalog", "catalog", "catalog_name"),
            "target_schema": ("target_schema", "schema", "schema_name"),
            "target_table": ("target_table", "table", "table_name"),
            "record_id": ("record_id", "registro_id", "id_registro", "recordid"),
            "action": (
                "operation",
                "action",
                "operacao",
                "acao",
                "event_type",
                "operation_type",
                "tipo_operacao",
            ),
            "old_value": ("old_value", "before_value", "previous_value", "valor_antigo"),
            "new_value": ("new_value", "after_value", "current_value", "valor_novo"),
            "performed_at": (
                "performed_at",
                "changed_at",
                "timestamp",
                "event_at",
                "event_timestamp",
                "operation_timestamp",
                "data_hora",
                "created_at",
            ),
            "performed_by": (
                "performed_by",
                "changed_by",
                "user",
                "usuario",
                "username",
                "user_email",
                "email",
                "created_by",
            ),
        }
        selected = {
            target: next((name for name in names if name in audit_columns), None)
            for target, names in aliases.items()
        }
        missing = [
            target
            for target, column in selected.items()
            if column is None
        ]
        if missing:
            expected = {
                "audit_id": "audit_id",
                "target_catalog": "target_catalog",
                "target_schema": "target_schema",
                "target_table": "target_table",
                "record_id": "record_id",
                "action": "operation",
                "old_value": "old_value",
                "new_value": "new_value",
                "performed_at": "performed_at",
                "performed_by": "performed_by",
            }
            raise RuntimeError(
                "app_audit sem colunas obrigatorias: "
                f"{', '.join(expected[target] for target in missing)}"
            )

        return {
            target: quote_identifier(column)
            for target, column in selected.items()
            if column is not None
        }
