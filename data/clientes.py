import pandas as pd
from config import BASE_CLIENTES
import streamlit as st

@st.cache_data
def load_clientes():
    base_clientes = BASE_CLIENTES
    if base_clientes.exists():
        df = pd.read_parquet(base_clientes)

        # Formatar data
        df['data_ultima_compra'] = df['data_ultima_compra'].dt.strftime('%d/%m/%Y')

        # Converter media_intervalo para inteiro
        if 'media_intervalo' in df.columns:
            df['media_intervalo'] = df['media_intervalo'].astype(int)

        # Excluir status_ciclo se existir
        df = df.drop(columns=['status_ciclo'], errors='ignore')

        # Renomear colunas
        df.rename(columns={
            'codigo cliente': 'codigo',
            'razao social': 'nome',
            'data_proxima_compra': 'proxima compra',
            'media_intervalo': 'periodo compra',
            'dias_para_proxima_compra': 'dias prox compra',
            'data_ultima_compra': 'ultima compra'
        }, inplace=True)

        # Criar a coluna 'codigo_loja' combinando 'codigo' e 'loja'
        df['codigo_loja'] = df['codigo'].astype(str) + "_" + df['loja'].astype(str)

        # Organizar as colunas na ordem desejada
        colunas_ordenadas = [
            'codigo', 'loja', 'codigo_loja', 'nome', 'setor', 'cidade', 'estado',
            'ultima compra', 'proxima compra', 'periodo compra', 'dias prox compra', 'status'
        ]
        df = df[[col for col in colunas_ordenadas if col in df.columns]]
        
        print("Arquivo clientes carregado com sucesso!")
        return df
    else:
        print(f"O arquivo não foi encontrado em: {base_clientes}")
        return None
