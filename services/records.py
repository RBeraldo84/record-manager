import json
from functools import lru_cache

import streamlit as st

from config import get_settings
from repositories.audit_repository import AuditRepository
from repositories.records_repository import RecordsRepository


@st.cache_data(ttl=30)
def list_records():
    return _records_repository().list_records()


def _audit(record_id, action, user):
    """Persist an audit event independently from the record mutation."""
    try:
        _audit_repository().create_event(record_id, action, user)
    except Exception as exc:
        raise RuntimeError(
            f"Registro salvo, mas a auditoria {action} falhou: {exc}"
        ) from exc


def _audit_change(record_id, action, user, old_value=None, new_value=None):
    """Persist an audit event with optional before/after record snapshots."""
    try:
        _audit_repository().create_event(
            record_id,
            action,
            user,
            _to_json(old_value),
            _to_json(new_value),
        )
    except Exception as exc:
        raise RuntimeError(
            f"Registro salvo, mas a auditoria {action} falhou: {exc}"
        ) from exc


def insert_record(codigo, descricao, status, user):
    record_id = _records_repository().insert_record(
        codigo,
        descricao,
        status,
        user,
    )
    if record_id is None:
        raise ValueError("Registro já existe para este código.")

    _audit_change(
        record_id,
        "INSERT",
        user,
        new_value={
            "id": record_id,
            "codigo": codigo,
            "descricao": descricao,
            "status": status,
            "created_by": user,
        },
    )
    list_records.clear()


def update_record(record_id, codigo, descricao, status, user):
    old_value = _records_repository().get_record(record_id)
    updated = _records_repository().update_record(
        record_id,
        codigo,
        descricao,
        status,
        user,
    )
    if not updated:
        raise ValueError("Registro já existe para este código.")

    _audit_change(
        record_id,
        "UPDATE",
        user,
        old_value=old_value,
        new_value={
            "id": record_id,
            "codigo": codigo,
            "descricao": descricao,
            "status": status,
            "updated_by": user,
        },
    )
    list_records.clear()


def delete_record(record_id, user):
    old_value = _records_repository().get_record(record_id)
    _records_repository().delete_record(record_id)
    _audit_change(
        record_id,
        "DELETE",
        user,
        old_value=old_value,
    )
    list_records.clear()


def _to_json(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


@lru_cache(maxsize=1)
def _records_repository() -> RecordsRepository:
    return RecordsRepository(get_settings().tables.records_full_name)


@lru_cache(maxsize=1)
def _audit_repository() -> AuditRepository:
    tables = get_settings().tables
    return AuditRepository(
        audit_table=tables.audit_full_name,
        target_catalog=tables.catalog,
        target_schema=tables.schema,
        target_table=tables.records_table,
    )
