import pandas as pd
import random
import json
import os
from datetime import date, timedelta, datetime
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
    print("🔄 Iniciando atribuição de clientes...")
    
    # Inicializa o cliente do Google Drive
    gdrive_client = GoogleDriveClient()
    
    # Define os IDs de pasta
    pasta_clientes = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    pasta_atribuidos = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    
    # Carregar dados dos clientes (parquet)
    if os.path.exists(CAMINHO_CLIENTES):
        print(f"📁 Arquivo de clientes encontrado localmente em {CAMINHO_CLIENTES}")
        df = pd.read_parquet(CAMINHO_CLIENTES)
    else:
        print("📥 Arquivo de clientes não encontrado localmente. Baixando do Google Drive...")
        if not os.path.exists('temp_data'):
            os.makedirs('temp_data')
        arquivos = gdrive_client.list_files(folder_id=pasta_clientes)
        arquivo_encontrado = next((f for f in arquivos if f['name'] == 'clientes_dash_televendas.parquet'), None)

        if not arquivo_encontrado:
            print("❌ Arquivo de clientes não encontrado no Google Drive.")
            return

        file_id = arquivo_encontrado['id']
        gdrive_client.download_file(file_id, CAMINHO_CLIENTES)
        df = pd.read_parquet(CAMINHO_CLIENTES)

    # Verificação de colunas
    if 'codigo cliente' not in df.columns or 'status' not in df.columns or 'loja' not in df.columns:
        raise ValueError("O DataFrame deve conter as colunas 'codigo cliente', 'status' e 'loja'")

    # Preparação dos dados
    df['codigo_loja'] = df['codigo cliente'].astype(str) + '_' + df['loja'].astype(str)
    df = df[['codigo_loja', 'status']].drop_duplicates()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Buscar o arquivo mais recente de atribuições no Google Drive
    print("🔍 Buscando arquivo mais recente de atribuições...")
    arquivos_atribuidos = gdrive_client.list_files(folder_id=pasta_atribuidos)
    arquivos_filtrados = [
        f for f in arquivos_atribuidos 
        if f['name'].startswith("clientes_atribuidos_") and f['name'].endswith(".json")
    ]
    arquivos_ordenados = sorted(arquivos_filtrados, key=lambda x: x['name'], reverse=True)
    arquivo_mais_recente = arquivos_ordenados[0] if arquivos_ordenados else None

    if arquivo_mais_recente:
        print(f"📄 Arquivo mais recente encontrado: {arquivo_mais_recente['name']}")
        gdrive_client.download_file(arquivo_mais_recente['id'], CAMINHO_JSON)
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        print("⚠️ Nenhum arquivo de atribuição encontrado. Criando novo do zero.")
        clientes_atribuidos = {}

    # Verifica a última data
    ultima_data = max([date.fromisoformat(d) for d in clientes_atribuidos.keys()], default=None)
    if ultima_data and ultima_data >= date.today():
        print("✅ Atribuição já realizada para hoje ou futuro.")
        return

    # Filtrar clientes ainda não atribuídos
    clientes_ja_atribuidos = set()
    for dia in clientes_atribuidos.values():
        for usuarios in dia.values():
            for cliente in usuarios:
                clientes_ja_atribuidos.add(cliente['codigo_loja'])

    clientes_disponiveis = df[~df['codigo_loja'].isin(clientes_ja_atribuidos)].copy()

    # Gerar novas atribuições
    for i in range(NUM_DIAS):
        data_str = str(DATA_INICIAL + timedelta(days=i))
        if data_str in clientes_atribuidos:
            continue

        clientes_atribuidos[data_str] = {}

        for usuario in USUARIOS:
            if len(clientes_disponiveis) < CLIENTES_POR_USUARIO:
                raise ValueError("⚠️ Não há clientes suficientes para atribuir.")

            amostra = clientes_disponiveis.sample(n=CLIENTES_POR_USUARIO, random_state=random.randint(0, 9999))
            clientes_disponiveis = clientes_disponiveis.drop(amostra.index)
            clientes_atribuidos[data_str][usuario] = amostra.to_dict(orient='records')

    # Salvar localmente
    with open(CAMINHO_JSON, "w") as f:
        json.dump(clientes_atribuidos, f, indent=4)

    # Criar nome com data/hora para upload
    agora_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo_novo = f"clientes_atribuidos_{agora_str}.json"
    gdrive_client.upload_file(CAMINHO_JSON, pasta_atribuidos, nome_arquivo_novo)

    print(f"✅ Atribuição concluída e arquivo salvo como {nome_arquivo_novo} no Google Drive.")
