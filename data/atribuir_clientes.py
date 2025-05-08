import pandas as pd
import random
import json
import os
from datetime import date, timedelta
from config import GoogleDriveClient

# ==== CONFIGURAÇÕES ====
CAMINHO_CLIENTES = os.path.join("temp_data", "clientes_dash_televendas.parquet")
CAMINHO_JSON = "temp_data/clientes_atribuidos.json"
USUARIOS = ["Franciele", "Julia", "Erica"]
CLIENTES_POR_USUARIO = 15
NUM_DIAS = 5
DATA_INICIAL = date.today()

def atribuir_clientes():
    """Carrega os dados dos clientes a partir do Google Drive e atribui aleatoriamente para os usuários."""
    # Inicializa o cliente do Google Drive
    gdrive_client = GoogleDriveClient()
    
    # Define o ID da pasta e o nome do arquivo
    pasta_clientes = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    base_clientes = 'clientes_dash_televendas.parquet'

    pasta_atribuidos = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    base_atribuidos = 'clientes_atribuidos.json'
    
    # Verifica se o arquivo de clientes já existe localmente
    if os.path.exists(CAMINHO_CLIENTES):
        print(f"Arquivo de clientes encontrado localmente em {CAMINHO_CLIENTES}. Carregando dados...")
        df = pd.read_parquet(CAMINHO_CLIENTES)
    else:
        print("Arquivo de clientes não encontrado localmente. Baixando do Google Drive...")
        
        # Cria o diretório 'temp_data' caso não exista
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
            print("Arquivo de clientes não encontrado no Google Drive.")
            return

    # Verificando se as colunas necessárias existem
    if 'codigo cliente' not in df.columns or 'status' not in df.columns or 'loja' not in df.columns:
        raise ValueError("O DataFrame deve conter as colunas 'codigo cliente', 'status' e 'loja'")

    # Combina 'codigo cliente' e 'loja' para criar uma chave única
    df['codigo_loja'] = df['codigo cliente'].astype(str) + '_' + df['loja'].astype(str)

    # Selecionar as colunas necessárias e remover duplicatas
    df = df[['codigo_loja', 'status']].drop_duplicates()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Embaralhar

    # Verificar se o arquivo JSON de atribuições já existe no Google Drive
    arquivos_atribuidos = gdrive_client.list_files(folder_id=pasta_atribuidos)
    arquivo_encontrado_atribuidos = next((f for f in arquivos_atribuidos if f['name'] == base_atribuidos), None)

    if arquivo_encontrado_atribuidos:
        file_id = arquivo_encontrado_atribuidos['id']
        gdrive_client.download_file(file_id, CAMINHO_JSON)
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        print(f"Arquivo {base_atribuidos} não encontrado no Google Drive. Criando um novo arquivo localmente.")
        clientes_atribuidos = {}

    # Verificar a última data atribuída
    ultima_data = max([date.fromisoformat(d) for d in clientes_atribuidos.keys()], default=None)

    if ultima_data and ultima_data >= date.today():
        print("Atribuição já realizada para hoje ou futuro.")
        return

    # Filtrar clientes não atribuídos
    clientes_ja_atribuidos = set()
    for dia in clientes_atribuidos.values():
        for clientes_usuario in dia.values():
            for cliente in clientes_usuario:
                clientes_ja_atribuidos.add(cliente['codigo_loja'])

    clientes_disponiveis = df[~df['codigo_loja'].isin(clientes_ja_atribuidos)].copy()

    # Gerar novas atribuições para os próximos dias
    for i in range(NUM_DIAS):
        data_str = str(DATA_INICIAL + timedelta(days=i))
        if data_str in clientes_atribuidos:
            continue  # Pula se já foi gerado

        clientes_atribuidos[data_str] = {}

        for usuario in USUARIOS:
            if len(clientes_disponiveis) < CLIENTES_POR_USUARIO:
                raise ValueError("Não há clientes suficientes para nova atribuição.")

            amostra = clientes_disponiveis.sample(n=CLIENTES_POR_USUARIO, random_state=random.randint(0, 9999))
            clientes_disponiveis = clientes_disponiveis.drop(amostra.index)

            clientes_atribuidos[data_str][usuario] = amostra.to_dict(orient='records')

    # Salvar o arquivo JSON atualizado localmente
    with open(CAMINHO_JSON, "w") as f:
        json.dump(clientes_atribuidos, f, indent=4)

    # Agora, faz o upload do arquivo JSON atualizado para o Google Drive
    gdrive_client.upload_file(CAMINHO_JSON, pasta_atribuidos)

    print(f"✅ Atribuição de clientes concluída para os próximos {NUM_DIAS} dias e arquivo JSON atualizado no Google Drive.")
