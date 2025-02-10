# tenant_storage.py
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from .middleware import get_media_settings  # Assurez-vous que le chemin d'import est correct

class TenantFileSystemStorage(FileSystemStorage):
    """
    Storage backend qui détermine dynamiquement le MEDIA_ROOT et MEDIA_URL
    en fonction du tenant courant, stockés dans le thread‑local.
    """
    def __init__(self, *args, **kwargs):
        # Récupérer les valeurs configurées pour la requête en cours
        media_root, media_url = get_media_settings()
        # Si aucune valeur spécifique n'est définie, utiliser les settings globaux
        location = media_root if media_root else settings.MEDIA_ROOT
        base_url = media_url if media_url else settings.MEDIA_URL
        super().__init__(location, base_url, *args, **kwargs)
