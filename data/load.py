import os
from data.historico_compras import load_historico
from data.clientes import load_clientes
import streamlit as st

@st.cache_data
def load_data():
    dados_clientes = load_clientes()
    dados_historico = load_historico()
    return dados_clientes, dados_historico

dados_clientes, dados_historico = load_data()

CAMINHO_JSON = os.path.join("temp_data", "clientes_atribuidos.json")

