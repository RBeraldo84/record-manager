import streamlit as st

from ui.components import load_css, render_hero, render_page_link, render_section_title

load_css()

render_hero(
    "Guia de uso",
    "Como consultar, criar, editar e excluir registros na página principal.",
)

render_page_link(
    "screens/parametros.py",
    label="Voltar para Parâmetros",
    icon=":material/arrow_back:",
    hint="Retorne para a tela principal de registros.",
)

render_section_title("Buscar registros", "Localize um registro pelo código ou descrição")
st.markdown(
    "Digite um termo no campo **Buscar registros** para filtrar a tabela por código ou "
    "descrição. O contador acima da tabela mostra quantos registros correspondem à busca."
)

render_section_title("Criar um registro", "Adicione um novo parâmetro à tabela")
st.markdown(
    "Clique em **+ Novo registro**, preencha **Código**, **Descrição** e **Status**, e "
    "clique em **Salvar registro**. O código não pode se repetir entre registros existentes."
)

render_section_title("Editar um registro", "Altere os dados de um registro existente")
st.markdown(
    "Na linha do registro desejado, clique no ícone **✎** (Ações), ajuste os campos e "
    "confirme em **Salvar alterações**."
)

render_section_title("Excluir um registro", "Remova um registro permanentemente")
st.markdown(
    "Na linha do registro desejado, clique no ícone **🗑** (Ações) e confirme a exclusão. "
    "Essa ação não pode ser desfeita."
)

render_section_title("Atualizar a lista", "Buscar os dados mais recentes")
st.markdown(
    "Clique em **Atualizar** a qualquer momento para recarregar a tabela com os dados "
    "mais recentes da base."
)

st.markdown(
    '<div class="rm-footer-watermark">Desenvolvido pelo time de dados - SLP</div>',
    unsafe_allow_html=True,
)
