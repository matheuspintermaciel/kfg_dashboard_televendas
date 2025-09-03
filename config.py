import base64
import json
from pathlib import Path
import os
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

import streamlit as st

# from dotenv import load_dotenv
# load_dotenv()

google_credentials = {
    "type": "service_account",
    "project_id": st.secrets["google"]["GOOGLE_PROJECT_ID"],
    "private_key_id": st.secrets["google"]["GOOGLE_PRIVATE_KEY_ID"],
    "private_key": st.secrets["google"]["GOOGLE_PRIVATE_KEY"],
    "client_email": st.secrets["google"]["GOOGLE_CLIENT_EMAIL"],
    "client_id": st.secrets["google"]["GOOGLE_CLIENT_ID"],
    "auth_uri": st.secrets["google"]["GOOGLE_AUTH_URI"],
    "token_uri": st.secrets["google"]["GOOGLE_TOKEN_URI"],
    "auth_provider_x509_cert_url": st.secrets["google"]["GOOGLE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": st.secrets["google"]["GOOGLE_CLIENT_X509_CERT_URL"],
    "universe_domain": st.secrets["google"]["GOOGLE_UNIVERSE_DOMAIN"]
}

# google_credentials = {
#     "type": "service_account",
#     "project_id": os.getenv("GOOGLE_PROJECT_ID"),
#     "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
#     "private_key": os.getenv("GOOGLE_PRIVATE_KEY"),
#     "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
#     "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#     "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
#     "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
#     "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
#     "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
#     "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
# }

CAMINHO_JSON = "data/clientes_atribuidos.json"

class GoogleDriveClient:
    def __init__(self, credentials_path=None, credentials_dict=None):
        scopes = ['https://www.googleapis.com/auth/drive']

        # Se não vier por parâmetro, tenta pegar do ambiente
        if credentials_dict is None and credentials_path is None:
            try:
                credentials_dict = google_credentials
                print(f"{credentials_dict}")
            except json.JSONDecodeError:
                raise ValueError("GOOGLE_DRIVE_CREDENTIALS não é um JSON válido.")

        if credentials_dict:
            self.creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        elif credentials_path:
            self.creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
        else:
            raise ValueError("Você deve fornecer credentials_path, credentials_dict ou setar GOOGLE_DRIVE_CREDENTIALS.")

        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path, folder_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Criando o nome do arquivo com timestamp
        file_name_with_timestamp = f"{os.path.basename(file_path).split('.')[0]}_{timestamp}.json"
        
        file_metadata = {
            'name': file_name_with_timestamp,
            'parents': [folder_id] if folder_id else []
        }
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        return uploaded_file

    def download_file(self, file_id, destination_path):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return destination_path

    def list_files(self, folder_id=None, query=None, mime_type=None):
        q_parts = []
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        if mime_type:
            q_parts.append(f"mimeType='{mime_type}'")
        if query:
            q_parts.append(query)

        query_string = ' and '.join(q_parts)
        results = self.service.files().list(
            q=query_string,
            pageSize=1000,
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])

    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()
        return True

# Caminhos de arquivos
ASSETS_PATH = Path("assets")
LOGO_PATH = ASSETS_PATH / "KFG_Distribuidora_logo_CMYK.png"

# Estilos CSS
CSS_STYLES = """
<style>
    /* Modifica a largura da sidebar para 20% da tela */
    .css-1d391kg {  /* Classe da sidebar */
        width: 20% !important;
    }

    /* Ajuste o logo para não afetar a largura da sidebar */
    .css-1d391kg img {
        width: 80px;  /* Tamanho fixo do logo */
        margin-bottom: 1rem;
    }

    /* Modifica o tamanho padrão de modal do streamlit */
    div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
        width: 95vw;
    }

    /* Esconde elementos da sidebar */
    .st-emotion-cache-y6y7ju.em9zgd018,
    div[data-testid="stSidebarNav"],
    div[data-testid="stSidebarNavItems"],
    div[data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    
    /* Garante que cada botão ocupe todo o card e tenha padding bottom */
    .stButton > button {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding-bottom: 160px;
            opacity: 0;
            cursor: pointer;
            z-index: 1;
        }
    /* Container relativo para posicionamento do botão */
    .card-container { position: relative; }
</style>
"""

CARD_STYLES = """
<style>
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 1.5rem;
    }
</style>
"""


def get_logo_base64():
    """Converte a imagem do logo para base64"""
    return base64.b64encode(LOGO_PATH.read_bytes()).decode()