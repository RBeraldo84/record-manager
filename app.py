from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Atualização de parâmetros",
    page_icon=str(Path(__file__).parent / "assets" / "b3.png"),
    layout="wide",
)

pg = st.navigation(
    [
        st.Page("screens/parametros.py", title="Atualização de parâmetros", default=True),
        st.Page("screens/guia.py", title="Guia de uso"),
    ],
    position="hidden",
)
pg.run()
