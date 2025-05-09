from datetime import datetime
import os
import pandas as pd
from config import GoogleDriveClient
#import streamlit as st

#@st.cache_data
def load_historico():
    """Carrega os dados dos clientes a partir do Google Drive."""
    # Inicializa o cliente do Google Drive
    gdrive_client = GoogleDriveClient()
    
    # Define o ID da pasta e o nome do arquivo
    pasta_clientes = '1IeUISCB-lWQ5TWS5dykmpmMjK2W6CtLD'
    base_clientes = 'vendas_mes_ano.parquet'

    temp_data_path = 'temp_data'
    if not os.path.exists(temp_data_path):
        os.makedirs(temp_data_path)

    # Caminho local completo
    file_path = os.path.join(temp_data_path, base_clientes)

    # Lista os arquivos da pasta e verifica se o desejado está lá
    arquivos = gdrive_client.list_files(folder_id=pasta_clientes)
    arquivo_encontrado = next((f for f in arquivos if f['name'] == base_clientes), None)

    if arquivo_encontrado:
        file_id = arquivo_encontrado['id']
        gdrive_client.download_file(file_id, file_path)
        df = pd.read_parquet(file_path)
    else:
        print("Arquivo não encontrado no Google Drive.")
        return None
    
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
