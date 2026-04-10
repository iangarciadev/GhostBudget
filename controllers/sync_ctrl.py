from state import AppState
from sync.gdrive import GDriveSync
from i18n import t


def upload(state: AppState) -> str:
    """Faz upload do banco para o Google Drive. Retorna mensagem de status."""
    gdrive = GDriveSync()
    gdrive.upload()
    return t("sync.upload_ok")


def download(state: AppState) -> str:
    """Baixa o banco do Google Drive e recarrega o estado."""
    gdrive = GDriveSync()
    gdrive.download()
    state.reload()
    return t("sync.download_ok")


def link_account() -> str:
    """Inicia o fluxo OAuth2. Retorna mensagem de status."""
    gdrive = GDriveSync()
    gdrive.authenticate()
    return t("sync.link_ok")


def is_linked() -> bool:
    return GDriveSync.credentials_exist()
