from state import AppState
from sync.gdrive import GDriveSync


def upload(state: AppState) -> str:
    """Faz upload do banco para o Google Drive. Retorna mensagem de status."""
    gdrive = GDriveSync()
    gdrive.upload()
    return "Backup enviado ao Google Drive com sucesso."


def download(state: AppState) -> str:
    """Baixa o banco do Google Drive e recarrega o estado."""
    gdrive = GDriveSync()
    gdrive.download()
    state.reload()
    return "Dados restaurados do Google Drive com sucesso."


def link_account() -> str:
    """Inicia o fluxo OAuth2. Retorna mensagem de status."""
    gdrive = GDriveSync()
    gdrive.authenticate()
    return "Conta Google vinculada com sucesso."


def is_linked() -> bool:
    return GDriveSync.credentials_exist()
