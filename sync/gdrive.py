"""
Google Drive sync para o GhostBudget.

Requer um projeto no Google Cloud Console com a Drive API habilitada e
um arquivo credentials.json (OAuth 2.0 Desktop App) na raiz do projeto.
"""
from pathlib import Path
import os

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / "data" / "gdrive_token.json"
DB_FILE = Path(__file__).parent.parent / "data" / "budget.db"
DRIVE_FOLDER_NAME = "GhostBudget"
DRIVE_FILE_NAME = "budget.db"


class GDriveSync:
    def __init__(self):
        self._service = None

    @staticmethod
    def credentials_exist() -> bool:
        return TOKEN_FILE.exists()

    def authenticate(self) -> None:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        import json

        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "Arquivo credentials.json não encontrado.\n"
                "Baixe-o do Google Cloud Console e coloque na raiz do projeto."
            )

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
        self._service = self._build_service(creds)

    def _load_service(self):
        if self._service:
            return self._service
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        if not TOKEN_FILE.exists():
            raise PermissionError("Conta Google não vinculada. Faça a autenticação primeiro.")

        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())

        self._service = self._build_service(creds)
        return self._service

    @staticmethod
    def _build_service(creds):
        from googleapiclient.discovery import build
        return build("drive", "v3", credentials=creds)

    def _get_or_create_folder(self) -> str:
        service = self._load_service()
        results = service.files().list(
            q=f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id)",
        ).execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]

        folder = service.files().create(
            body={"name": DRIVE_FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"},
            fields="id",
        ).execute()
        return folder["id"]

    def upload(self) -> None:
        from googleapiclient.http import MediaFileUpload

        if not DB_FILE.exists():
            raise FileNotFoundError("Banco de dados não encontrado.")

        service = self._load_service()
        folder_id = self._get_or_create_folder()

        results = service.files().list(
            q=f"name='{DRIVE_FILE_NAME}' and '{folder_id}' in parents and trashed=false",
            fields="files(id)",
        ).execute()
        files = results.get("files", [])

        media = MediaFileUpload(str(DB_FILE), mimetype="application/octet-stream")

        if files:
            service.files().update(
                fileId=files[0]["id"], media_body=media
            ).execute()
        else:
            service.files().create(
                body={"name": DRIVE_FILE_NAME, "parents": [folder_id]},
                media_body=media,
                fields="id",
            ).execute()

    def download(self) -> None:
        import io
        from googleapiclient.http import MediaIoBaseDownload

        service = self._load_service()
        folder_id = self._get_or_create_folder()

        results = service.files().list(
            q=f"name='{DRIVE_FILE_NAME}' and '{folder_id}' in parents and trashed=false",
            fields="files(id)",
        ).execute()
        files = results.get("files", [])

        if not files:
            raise FileNotFoundError("Nenhum backup encontrado no Google Drive.")

        file_id = files[0]["id"]
        request = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        DB_FILE.parent.mkdir(exist_ok=True)
        DB_FILE.write_bytes(buf.getvalue())
