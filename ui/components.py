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


_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


@st.cache_data
def _read_css() -> str:
    css_path = _ASSETS_DIR / "style.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def load_css() -> None:
    css_text = _read_css()
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


def render_hero(title: str = "Controle de Parâmetros", subtitle: str = "") -> None:
    logo_src = _asset_data_uri("b3.png")
    logo_markup = ""
    if logo_src:
        logo_markup = (
            f'<div class="rm-logo-shell"><img src="{logo_src}" alt="B3" /></div>'
        )

    st.markdown(
        f"""<section class="rm-hero"><div class="rm-brand-lockup">{logo_markup}<div><p class="rm-kicker"></p><h1>{escape(title)}</h1><p class="rm-subtitle">{escape(subtitle)}</p></div></div></section>""",
        unsafe_allow_html=True,
    )


@st.cache_data
def _asset_data_uri(filename: str) -> str | None:
    asset_path = _ASSETS_DIR / filename
    if not asset_path.exists():
        return None
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_page_link(page: str, label: str, icon: str, hint: str) -> None:
    with st.container(border=True):
        st.page_link(page, label=label, icon=icon)
        st.markdown(f'<p class="rm-nav-hint">{escape(hint)}</p>', unsafe_allow_html=True)


def render_metrics(df: pd.DataFrame) -> None:
    total_records = len(df)
    active_records = 0
    if not df.empty and "status" in df.columns:
        status_series = df["status"].fillna("").astype(str).str.upper()
        active_records = int(status_series.eq("ATIVO").sum())
    inactive_records = total_records - active_records

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total_records)
    with col2:
        st.metric("Ativos", active_records)
    with col3:
        st.metric("Inativos", inactive_records)


_STATUS_FILTER_OPTIONS = {"Todos": None, "Ativos": "ATIVO", "Inativos": "INATIVO"}


def render_status_filter() -> str | None:
    """Renders a horizontal Todos/Ativos/Inativos filter.

    Returns the selected status filter ("ATIVO", "INATIVO", or None for all).
    """
    choice = st.radio(
        "Filtrar por status",
        options=list(_STATUS_FILTER_OPTIONS),
        horizontal=True,
        key="rm_status_filter_choice",
    )
    return _STATUS_FILTER_OPTIONS[choice]


def render_section_title(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="rm-section-title"><span>{escape(title)}</span><small>{escape(subtitle)}</small></div>',
        unsafe_allow_html=True,
    )


def filter_records(df: pd.DataFrame, search_term: str, status_filter: str | None = None) -> pd.DataFrame:
    result = df
    if status_filter and not df.empty and "status" in df.columns:
        result = result[result["status"].fillna("").astype(str).str.upper() == status_filter]

    if not search_term or result.empty:
        return result.copy()

    mask = (
        result["codigo"].fillna("").astype(str).str.contains(search_term, case=False, regex=False)
        | result["descricao"].fillna("").astype(str).str.contains(search_term, case=False, regex=False)
    )
    return result[mask]


def status_badge_html(status: str) -> str:
    value = (status or "").strip().upper()
    variant = "rm-status-active" if value == "ATIVO" else "rm-status-inactive"
    return f'<span class="rm-status-badge {variant}">{escape(value)}</span>'


def render_empty_state(search_term: str, status_filter: str | None = None) -> None:
    if search_term:
        title = "Nenhum registro encontrado"
        subtitle = f'Nenhum resultado para "{escape(search_term)}". Tente outro termo de busca.'
    elif status_filter:
        title = "Nenhum registro encontrado"
        subtitle = "Nenhum registro corresponde ao filtro selecionado acima."
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
