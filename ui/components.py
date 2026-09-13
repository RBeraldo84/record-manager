import base64
from html import escape
import os
from pathlib import Path

import pandas as pd
import streamlit as st


VISIBLE_COLUMNS = [
    "codigo",
    "descricao",
    "status",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
]
COLUMN_LABELS = {
    "codigo": "Código",
    "descricao": "Descrição",
    "status": "Status",
    "created_at": "Criado em",
    "created_by": "Criado por",
    "updated_at": "Atualizado em",
    "updated_by": "Atualizado por",
}


@st.cache_data
def _read_css(app_file: str) -> str:
    css_path = Path(app_file).parent / "assets" / "style.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def load_css(app_file: str) -> None:
    css_text = _read_css(app_file)
    if css_text:
        st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)


def format_timestamp(value) -> str:
    if value is None or pd.isna(value):
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)[:19]


def get_current_user() -> str:
    headers = st.context.headers
    for header_name in (
        "x-forwarded-email",
        "x-forwarded-preferred-username",
        "x-forwarded-user",
        "x-forwarded-name",
    ):
        value = headers.get(header_name)
        if value and value.strip():
            return value.strip()

    # Databricks Apps provides forwarded headers when user authorization is enabled.
    return os.getenv("DATABRICKS_USER", "Ambiente local")


def render_hero(app_file: str) -> None:
    logo_src = _asset_data_uri(app_file, "b3.png")
    logo_markup = ""
    if logo_src:
        logo_markup = (
            f'<div class="rm-logo-shell"><img src="{logo_src}" alt="B3" /></div>'
        )

    st.markdown(
        f"""<section class="rm-hero"><div class="rm-brand-lockup">{logo_markup}<div><p class="rm-kicker"></p><h1>Controle de Parâmetros</h1><p class="rm-subtitle"></p></div></div></section>""",
        unsafe_allow_html=True,
    )


@st.cache_data
def _asset_data_uri(app_file: str, filename: str) -> str | None:
    asset_path = Path(app_file).parent / "assets" / filename
    if not asset_path.exists():
        return None
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_metrics(df: pd.DataFrame, inactive_label: str = "Inativo") -> None:
    total_records = len(df)
    active_records = 0
    if not df.empty and "status" in df.columns:
        status_series = df["status"].fillna("").astype(str).str.upper()
        active_records = int(status_series.eq("ATIVO").sum())
    other_statuses = total_records - active_records

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total_records)
    with col2:
        st.metric("Ativos", active_records)
    with col3:
        st.metric(inactive_label, other_statuses)


def render_section_title(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="rm-section-title"><span>{escape(title)}</span><small>{escape(subtitle)}</small></div>',
        unsafe_allow_html=True,
    )


def filter_records(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    if not search_term or df.empty:
        return df.copy()

    mask = (
        df["codigo"].fillna("").astype(str).str.contains(search_term, case=False, regex=False)
        | df["descricao"].fillna("").astype(str).str.contains(search_term, case=False, regex=False)
    )
    return df[mask]


def status_badge_html(status: str) -> str:
    value = (status or "").strip().upper()
    variant = "rm-status-active" if value == "ATIVO" else "rm-status-inactive"
    return f'<span class="rm-status-badge {variant}">{escape(value)}</span>'


def render_empty_state(search_term: str) -> None:
    if search_term:
        title = "Nenhum registro encontrado"
        subtitle = f'Nenhum resultado para "{escape(search_term)}". Tente outro termo de busca.'
    else:
        title = "Nenhum registro cadastrado"
        subtitle = 'Use "+ Novo registro" para criar o primeiro registro desta base.'
    st.markdown(
        f'<div class="rm-empty-state"><strong>{title}</strong><span>{subtitle}</span></div>',
        unsafe_allow_html=True,
    )


def build_record_options(df: pd.DataFrame) -> dict[str, str]:
    return {
        f"{row.codigo} · {row.descricao}": row.id
        for row in df.itertuples(index=False)
    }
