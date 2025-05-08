import os
import pandas as pd
from config import GoogleDriveClient

# @st.cache_data
def load_clientes():
    """Carrega os dados dos clientes a partir do Google Drive."""
    # Inicializa o cliente do Google Drive
    gdrive_client = GoogleDriveClient()
    
    # Define o ID da pasta e o nome do arquivo
    pasta_clientes = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    base_clientes = 'clientes_dash_televendas.parquet'

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
