import os
import logging
from django.conf import settings
from django.db import connection
from django.apps import apps

logger = logging.getLogger(__name__)

class TenantUtils:
    @staticmethod
    def get_public_domains():
        """ Récupère tous les domaines publics définis dans les settings. """
        return getattr(settings, "TENANT_PUBLIC_DOMAINS", [])

    @staticmethod
    def get_domain(host):
        """ Récupère un domaine spécifique en fonction de l'hôte. """
        Domain = apps.get_model(settings.DOMAIN_MODEL)
        try:
            return Domain.objects.select_related("tenant").get(domain=host, is_primary=True)
        except Domain.DoesNotExist:
            return None

    @staticmethod
    def get_current_tenant(request):
        """ Retourne le tenant actif basé sur la requête. """
        return getattr(request, "tenant", None)

    @staticmethod
    def get_tenant_email_config(tenant):
        """ Récupère la configuration email d'un tenant. """
        if not tenant:
            return None
        
        EmailConfig = apps.get_model(settings.EMAIL_CONFIG_MODEL)
        return EmailConfig.objects.first()

    @staticmethod
    def set_tenant_media_root(schema_name):
        """ Définit `MEDIA_ROOT` spécifique au tenant. """
        tenant_media_root = os.path.join(settings.MEDIA_ROOT, schema_name)
        os.makedirs(tenant_media_root, exist_ok=True)
        settings.MEDIA_ROOT = tenant_media_root
        logger.info(f"MEDIA_ROOT défini sur {tenant_media_root}")

    @staticmethod
    def set_tenant_schema(schema_name):
        """ Définit dynamiquement le schéma PostgreSQL pour un tenant. """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO %s;", [schema_name])
        except Exception as e:
            logger.error(f"Erreur lors du changement de schéma: {str(e)}")
            return False
        return True
