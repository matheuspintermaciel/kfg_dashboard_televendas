from datetime import datetime
import pandas as pd
from config import BASE_HISTORICO
import streamlit as st

@st.cache_data
def load_historico():
    base_historico = BASE_HISTORICO
    if base_historico.exists():
        df = pd.read_parquet(base_historico, engine='pyarrow')
        df.rename(columns={
            'Produto_Codigo': 'codigo',
            'Produto_Descricao': 'descrição',
        }, inplace=True)
        df['Cliente_Codigo'] = df['Cliente_Codigo'].astype(str).str.strip()
        # Seleciona apenas as colunas de meses
        colunas_meses = [
            col for col in df.columns 
            if col not in ['Cliente_Codigo', 'A1_LOJA', 'codigo', 'descrição']
        ]

        # Ordena com base em datas reais
        colunas_ordenadas = sorted(
            colunas_meses, 
            key=lambda x: datetime.strptime(x, "%m/%y")
        )

        # Reorganiza o DataFrame com as colunas ordenadas
        df = df[['Cliente_Codigo', 'A1_LOJA', 'codigo', 'descrição'] + colunas_ordenadas]

        print("Arquivo historico carregado com sucesso!")
        return df
    else:
        print(f"O arquivo não foi encontrado em: {base_historico}")
        return None
