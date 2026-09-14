import pandas as pd
import streamlit as st

from config import get_settings
from services.records import delete_record, insert_record, list_records, update_record
from ui.components import (
    filter_records,
    format_timestamp,
    get_current_user,
    load_css,
    render_empty_state,
    render_hero,
    render_metrics,
    render_page_link,
    render_section_title,
    render_status_filter,
    status_badge_html,
)

load_css()
user = get_current_user()

render_hero()

render_page_link(
    "screens/guia.py",
    label="Guia de uso",
    icon=":material/menu_book:",
    hint="Abra esta página para ver instruções de uso.",
)

try:
    records = list_records()
    df = pd.DataFrame(records)
except Exception as exc:
    st.error(f"Não foi possível consultar a tabela: {exc}")
    st.stop()

render_metrics(df)
render_section_title(
    f"Tabela {get_settings().tables.records_table}",
    "Dados ordenados por registro mais recente",
)

status_filter = render_status_filter()

left, middle, right = st.columns([4, 1, 1])

with left:
    search = st.text_input(
        "Buscar registros",
        placeholder="Buscar por código ou descrição...",
    )

with middle:
    st.markdown('<div class="rm-action-spacer"></div>', unsafe_allow_html=True)
    refresh = st.button("Atualizar", use_container_width=True)

with right:
    st.markdown('<div class="rm-action-spacer"></div>', unsafe_allow_html=True)
    new_record = st.button(
        "+ Novo registro",
        use_container_width=True,
        type="primary",
    )

@st.dialog("Novo registro")
def new_record_dialog():
    with st.form("new_record_form"):
        form_code = st.text_input("Código", max_chars=100)
        form_description = st.text_area("Descrição", max_chars=1000)
        form_status = st.selectbox("Status", ["ATIVO", "INATIVO"])
        save_col, cancel_col = st.columns(2)
        with save_col:
            submitted = st.form_submit_button("Salvar registro", type="primary", use_container_width=True)
        with cancel_col:
            cancelled = st.form_submit_button("Cancelar", use_container_width=True)

        if submitted:
            if not form_code.strip() or not form_description.strip():
                st.error("Código e descrição são obrigatórios.")
            else:
                try:
                    with st.spinner("Salvando registro..."):
                        insert_record(form_code.strip(), form_description.strip(), form_status, user)
                    st.success("Registro criado e auditado.")
                    st.rerun()
                except Exception as exc:
                    st.warning(str(exc) if str(exc).startswith("Registro salvo") else f"Não foi possível criar o registro: {exc}")
        elif cancelled:
            st.rerun()


@st.dialog("Editar registro")
def edit_record_dialog(row):
    row_id = getattr(row, "id", None)
    with st.form(f"edit_record_form_{row_id}"):
        edit_code = st.text_input("Código", value=str(getattr(row, "codigo", "")))
        edit_description = st.text_area("Descrição", value=str(getattr(row, "descricao", "")))
        status_values = ["ATIVO", "INATIVO"]
        current_status = str(getattr(row, "status", "ATIVO")).upper()
        if current_status not in status_values:
            status_values.insert(0, current_status)
        edit_status = st.selectbox("Status", status_values, index=status_values.index(current_status))
        save_col, cancel_col = st.columns(2)
        with save_col:
            update_submitted = st.form_submit_button("Salvar alterações", type="primary", use_container_width=True)
        with cancel_col:
            cancel_edit = st.form_submit_button("Cancelar", use_container_width=True)

        if update_submitted:
            if not edit_code.strip() or not edit_description.strip():
                st.error("Código e descrição são obrigatórios.")
            else:
                try:
                    with st.spinner("Salvando alterações..."):
                        update_record(row_id, edit_code.strip(), edit_description.strip(), edit_status, user)
                    st.success("Registro atualizado e auditado.")
                    st.rerun()
                except Exception as exc:
                    st.warning(str(exc) if str(exc).startswith("Registro salvo") else f"Não foi possível atualizar o registro: {exc}")
        elif cancel_edit:
            st.rerun()


@st.dialog("Excluir registro")
def delete_record_dialog(row):
    row_id = getattr(row, "id", None)
    st.warning(f"Excluir o registro **{getattr(row, 'codigo', '')}**? A ação será auditada.")
    confirm_col, cancel_col = st.columns(2)
    with confirm_col:
        if st.button("Confirmar exclusão", type="primary", use_container_width=True, key="confirm_delete_action"):
            try:
                with st.spinner("Excluindo registro..."):
                    delete_record(row_id, user)
                st.success("Registro excluído e auditado.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível excluir o registro: {exc}")
    with cancel_col:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


if new_record:
    new_record_dialog()

if refresh:
    list_records.clear()
    st.rerun()

search_term = search.strip()
working_df = filter_records(df, search_term, status_filter)

if search_term:
    st.caption(f"{len(working_df)} de {len(df)} registros encontrados para “{search_term}”.")

if not working_df.empty:
    header = st.columns([1.25, 2.85, .85, 1.55, 1.55, 1.3])
    for column, label in zip(header, ["Código", "Descrição", "Status", "Criado em", "Criado por", "Ações"]):
        column.markdown(f'<span class="rm-table-heading">{label}</span>', unsafe_allow_html=True)

    with st.container(height=248):
        for row in working_df.itertuples(index=False):
            row_id = getattr(row, "id", None)
            values = st.columns([1.25, 2.85, .85, 1.55, 1.55, 1.3])
            values[0].write(str(getattr(row, "codigo", "")))
            values[1].write(str(getattr(row, "descricao", "")))
            values[2].markdown(status_badge_html(getattr(row, "status", "")), unsafe_allow_html=True)
            values[3].write(format_timestamp(getattr(row, "created_at", None)))
            values[4].write(str(getattr(row, "created_by", "")))

            edit_action, delete_action = values[5].columns(2)
            if edit_action.button("✎", key=f"edit_{row_id}", help="Editar registro"):
                edit_record_dialog(row)
            if delete_action.button("🗑", key=f"delete_{row_id}", help="Excluir registro"):
                delete_record_dialog(row)
else:
    render_empty_state(search_term, status_filter)

st.markdown(
    '<div class="rm-footer-watermark">Desenvolvido pelo time de dados - SLP</div>',
    unsafe_allow_html=True,
)
