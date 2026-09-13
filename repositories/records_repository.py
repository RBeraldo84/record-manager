from dataclasses import dataclass
from uuid import uuid4

from services.database import get_connection


@dataclass(frozen=True)
class RecordsRepository:
    records_table: str

    def get_record(self, record_id: str) -> dict | None:
        query = f"""
            SELECT
                id,
                codigo,
                descricao,
                status,
                created_at,
                created_by,
                updated_at,
                updated_by
            FROM {self.records_table}
            WHERE id = ?
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                columns = [column[0] for column in cursor.description]

        return dict(zip(columns, row))

    def list_records(self) -> list[dict]:
        query = f"""
            SELECT
                id,
                codigo,
                descricao,
                status,
                created_at,
                created_by,
                updated_at,
                updated_by
            FROM {self.records_table}
            ORDER BY created_at DESC
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    def insert_record(
        self,
        codigo: str,
        descricao: str,
        status: str,
        user: str,
    ) -> str | None:
        """Insert atomically, skipping if codigo already exists. Returns the new id, or None if it was a duplicate."""
        record_id = str(uuid4())
        query = f"""
            MERGE INTO {self.records_table} AS t
            USING (SELECT ? AS id, ? AS codigo, ? AS descricao, ? AS status, ? AS created_by) AS s
            ON lower(trim(t.codigo)) = lower(trim(s.codigo))
            WHEN NOT MATCHED THEN INSERT (id, codigo, descricao, status, created_at, created_by)
            VALUES (s.id, s.codigo, s.descricao, s.status, current_timestamp(), s.created_by)
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (record_id, codigo, descricao, status, user),
                )
                result = cursor.fetchone()
                inserted = bool(result and result.num_inserted_rows == 1)
            if hasattr(connection, "commit"):
                connection.commit()

        return record_id if inserted else None

    def update_record(
        self,
        record_id: str,
        codigo: str,
        descricao: str,
        status: str,
        user: str,
    ) -> bool:
        """Update atomically, skipping if codigo already belongs to another record. Returns whether the update applied."""
        query = f"""
            UPDATE {self.records_table} AS t
            SET
                codigo = ?,
                descricao = ?,
                status = ?,
                updated_at = current_timestamp(),
                updated_by = ?
            WHERE id = ?
              AND NOT EXISTS (
                SELECT 1 FROM {self.records_table} AS t2
                WHERE lower(trim(t2.codigo)) = lower(trim(?))
                  AND t2.id <> ?
              )
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (codigo, descricao, status, user, record_id, codigo, record_id),
                )
                result = cursor.fetchone()
                updated = bool(result and result.num_affected_rows == 1)
            if hasattr(connection, "commit"):
                connection.commit()

        return updated

    def delete_record(self, record_id: str) -> None:
        query = f"""
            DELETE FROM {self.records_table}
            WHERE id = ?
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
            if hasattr(connection, "commit"):
                connection.commit()
