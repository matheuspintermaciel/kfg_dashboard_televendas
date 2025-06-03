import streamlit as st
import json
import os
from data.atribuir_clientes import atribuir_clientes
from data.load import load_data

ARQUIVO_ATRIBUICAO = "data/clientes_atribuidos.json"
USUARIOS_PERMITIDOS = ["Franciele", "Julia", "Erica","Laysa", "Lenice"]

def login():
    col1, col2, col3 = st.columns([1, 4, 1])  # Layout centralizado com 6 partes

    with col2:
        st.image("assets/KFG_Distribuidora_logo_CMYK.png", use_container_width=True)
        st.markdown("## Acesso ao Painel de Clientes")

        with st.form("login_form"):
            usuario = st.selectbox("👤 Selecione seu nome", [""] + USUARIOS_PERMITIDOS)
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if entrar:
            if usuario == "":
                st.warning("⚠️ Por favor, selecione seu nome.")
            else:
                st.session_state["user_id"] = usuario
                st.session_state["user_name"] = usuario
                st.rerun()
