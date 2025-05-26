import pandas as pd
import random
import json
import os
from datetime import date, timedelta, datetime
from itertools import product
from config import GoogleDriveClient

# ==== CONFIGURAÇÕES ====
CAMINHO_CLIENTES = os.path.join("temp_data", "clientes_dash_televendas.parquet")
CAMINHO_JSON = os.path.join("temp_data", "clientes_atribuidos.json")
USUARIOS = ["Franciele", "Julia", "Erica"]
CLIENTES_POR_USUARIO = 15
NUM_DIAS = 5
DATA_INICIAL = date.today()

def atribuir_clientes():
    print("🔄 Iniciando atribuição de clientes...")

    gdrive_client = GoogleDriveClient()
    pasta_clientes = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    pasta_atribuidos = '1SGB1HO0MQxUoJcBAEicTmxxE4hg_y47E'
    os.makedirs("temp_data", exist_ok=True)

    if os.path.exists(CAMINHO_CLIENTES):
        print(f"📁 Arquivo de clientes encontrado localmente em {CAMINHO_CLIENTES}")
        df = pd.read_parquet(CAMINHO_CLIENTES)
    else:
        print("📅 Baixando clientes do Google Drive...")
        arquivos = gdrive_client.list_files(folder_id=pasta_clientes)
        arquivo_encontrado = next((f for f in arquivos if f['name'] == 'clientes_dash_televendas.parquet'), None)
        if not arquivo_encontrado:
            print("❌ Arquivo de clientes não encontrado no Google Drive.")
            return
        gdrive_client.download_file(arquivo_encontrado['id'], CAMINHO_CLIENTES)
        df = pd.read_parquet(CAMINHO_CLIENTES)

    if 'codigo cliente' not in df.columns or 'status' not in df.columns or 'loja' not in df.columns:
        raise ValueError("O DataFrame deve conter as colunas 'codigo cliente', 'status' e 'loja'")

    df['codigo_loja'] = df['codigo cliente'].astype(str) + '_' + df['loja'].astype(str)
    df = df[['codigo_loja', 'status']].drop_duplicates()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"📦 Total de clientes únicos disponíveis: {len(df)}")

    print("🔍 Verificando atribuições anteriores...")
    arquivos_atribuidos = gdrive_client.list_files(folder_id=pasta_atribuidos)
    arquivos_filtrados = [
        f for f in arquivos_atribuidos
        if f['name'].startswith("clientes_atribuidos_") and f['name'].endswith(".json")
    ]
    arquivos_ordenados = sorted(arquivos_filtrados, key=lambda x: x['name'], reverse=True)
    arquivo_mais_recente = arquivos_ordenados[0] if arquivos_ordenados else None

    if arquivo_mais_recente:
        print(f"📄 Último arquivo encontrado: {arquivo_mais_recente['name']}")
        gdrive_client.download_file(arquivo_mais_recente['id'], CAMINHO_JSON)
        with open(CAMINHO_JSON, "r") as f:
            clientes_atribuidos = json.load(f)
    else:
        print("📂 Nenhum histórico de atribuições encontrado. Iniciando novo.")
        clientes_atribuidos = {}

    ultima_data = max([date.fromisoformat(d) for d in clientes_atribuidos.keys()], default=None)
    if ultima_data and ultima_data >= date.today():
        print("✅ Atribuições já realizadas para hoje ou datas futuras.")
        return

    clientes_ja_atribuidos = set()
    for dia in clientes_atribuidos.values():
        for usuarios in dia.values():
            for cliente in usuarios:
                clientes_ja_atribuidos.add(cliente['codigo_loja'])

    clientes_disponiveis = df[~df['codigo_loja'].isin(clientes_ja_atribuidos)].copy()
    print(f"🌟 Clientes disponíveis para novas atribuições: {len(clientes_disponiveis)}")

    dias = [str(DATA_INICIAL + timedelta(days=i)) for i in range(NUM_DIAS)]
    alocacoes = list(product(dias, USUARIOS))
    slots = len(alocacoes) * CLIENTES_POR_USUARIO
    clientes_disponiveis = clientes_disponiveis.head(slots)

    destinos = []
    for dia, usuario in alocacoes:
        destinos.extend([(dia, usuario)] * CLIENTES_POR_USUARIO)
    destinos = destinos[:len(clientes_disponiveis)]

    clientes_disponiveis = clientes_disponiveis.copy()
    clientes_disponiveis["dia"], clientes_disponiveis["usuario"] = zip(*destinos)

    for dia, grupo_usuarios in clientes_disponiveis.groupby("dia"):
        if dia not in clientes_atribuidos:
            clientes_atribuidos[dia] = {}
        for usuario, df_user in grupo_usuarios.groupby("usuario"):
            clientes_atribuidos[dia][usuario] = df_user.drop(columns=["dia", "usuario"]).to_dict(orient="records")

    with open(CAMINHO_JSON, "w") as f:
        json.dump(clientes_atribuidos, f, indent=4)

    gdrive_client.upload_file(CAMINHO_JSON, pasta_atribuidos)

    print("✅ Atribuição concluída com sucesso!")