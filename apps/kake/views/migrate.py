from celery import shared_task
from django.core.management import call_command
from django.db import connection
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
import re

@shared_task
def migrate_tenant(schema_name, name, domain, user_id):
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        print(f"Utilisateur récupéré : {user.username}, Email : {user.email}")

        # Assainir le nom du schéma pour PostgreSQL
        schema_name = re.sub(r'\W|^(?=\d)', '_', schema_name)
        if not schema_name.isidentifier():
            raise ValidationError("Nom du schéma invalide.")

        # Exécuter la création et migration du schéma dans une transaction indépendante
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

        # Ouvrir une nouvelle connexion temporaire et définir le search_path
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {schema_name};")
            call_command('migrate', database='default', interactive=False)

        if not user.email:
            raise ValueError("L'utilisateur doit avoir un email.")

        # Création de l'utilisateur spécifique au tenant
        new_user = User(
            username=user.username or f"default_{user.id}",
            email=user.email,
            password=user.password,
            role='admin',
            is_active=True
        )  # Hacher le mot de passe
        new_user.save()

        # Mise à jour du site dans le bon schéma
        Site.objects.update_or_create(
            domain=domain,
            defaults={"name": name},
        )

        return f"Migrations du tenant {schema_name} terminées avec succès."

    except Exception as e:
        # Supprimer le schéma si erreur
        with connection.cursor() as cursor:
            cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
        raise ValidationError(f"Erreur critique : {str(e)}")
    finally:
        # Réinitialiser le search_path sur la connexion isolée et fermer cette connexion
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public;")
        except Exception as e_reset:
            print("Erreur lors du reset du search_path:", e_reset)
        finally:
            # Fermer la connexion pour qu'elle ne soit pas réutilisée par d'autres processus
            connection.close()
