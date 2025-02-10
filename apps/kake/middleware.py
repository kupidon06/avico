import os
import logging
from django.db import connection
from django.shortcuts import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.apps import apps

# Initialiser un logger
logger = logging.getLogger(__name__)
created_media_directories = {}

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """ Gère le tenant en fonction du domaine et configure dynamiquement les emails et médias. """

        # Obtenir le domaine de l'hôte (sans le port)
        host = request.get_host().split(":")[0]
        logger.info(f"Requête entrante sur le domaine: {host}")

        # Récupérer les modèles nécessaires
        Tenant = apps.get_model(settings.TENANT_MODEL)
        Domain = apps.get_model(settings.DOMAIN_MODEL)
        EmailConfig = apps.get_model(settings.EMAIL_CONFIG_MODEL)

        # Vérifier si l'URL est celle de la page 404 pour éviter une boucle infinie
        try:
            error_404_url = reverse(settings.URL404).lstrip("/")
            if request.path.lstrip("/") == error_404_url:
                return  # Ne rien faire, laisser Django gérer la page 404
        except Exception:
            return HttpResponseForbidden("Error configuring tenant: Invalid 404 URL")

        # Liste des domaines publics
        public_domains = getattr(settings, "TENANT_PUBLIC_DOMAINS", [])

        # Vérifier si l'hôte est un domaine public
        if host in public_domains:
            schema_name = "public"
            request.tenant = None
            request.domain = settings.MAIN_DOMAIN
            request.urlconf = getattr(settings, "ROOT_URLCONF")  # URLs publiques
            request.tenant_media_root = settings.MEDIA_ROOT
            request.tenant_media_url = settings.MEDIA_URL
        else:
            try:
                # Rechercher le domaine dans la base de données
                domain_entry = Domain.objects.select_related("tenant").get(domain=host, is_primary=True)
                tenant = domain_entry.tenant
                schema_name = tenant.schema_name
                request.tenant = tenant
                request.domain = domain_entry
                request.urlconf = getattr(settings, "TENANT_URLCONF")  # URLs locataires

                # Définir les valeurs dynamiques
                request.tenant_media_root, request.tenant_media_url = self.get_media_paths(schema_name)

                # Charger la configuration email du tenant
                self.configure_email(tenant, EmailConfig)

            except Domain.DoesNotExist:
                logger.error(f"Domaine {host} non trouvé, redirection vers la page 404.")
                return HttpResponseRedirect(reverse(settings.URL404))

        # Changer le schéma dans PostgreSQL
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO %s;", [schema_name])
        except Exception as e:
            logger.error(f"Erreur de configuration du tenant {host}: {str(e)}")
            return HttpResponseForbidden(f"Error configuring tenant: {str(e)}")

    def get_media_paths(self, schema_name):
        """ Retourne le chemin MEDIA_ROOT et MEDIA_URL spécifiques au tenant. """
        global created_media_directories

        tenant_media_root = os.path.join(settings.MEDIA_ROOT, schema_name)
        tenant_media_url = f"/media/{schema_name}/"

        if schema_name not in created_media_directories:
            os.makedirs(tenant_media_root, exist_ok=True)
            created_media_directories[schema_name] = tenant_media_root
            logger.info(f"MEDIA_ROOT défini sur {tenant_media_root}")

        return tenant_media_root, tenant_media_url

    def configure_email(self, tenant, EmailConfig):
        """ Configure dynamiquement les paramètres email pour le tenant. """
        email_config = EmailConfig.objects.all().first()
        if email_config:
            settings.EMAIL_HOST = email_config.email_host
            settings.EMAIL_PORT = email_config.email_port
            settings.EMAIL_USE_TLS = email_config.email_use_tls
            settings.EMAIL_HOST_USER = email_config.email_host_user
            settings.EMAIL_HOST_PASSWORD = email_config.email_host_password
            settings.DEFAULT_FROM_EMAIL = email_config.default_from_email
