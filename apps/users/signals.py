from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.signing import Signer, TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from .models import User

signer = TimestampSigner()

@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:  # Seulement lors de la création d'un nouvel utilisateur
        # Générer un token signé
        token = signer.sign(instance.email)
        
        # Générer le lien de confirmation
        confirmation_link = reverse('confirm_email', args=[token])
        full_link = f"{settings.SITE_URL}{confirmation_link}"

        # Envoyer l'email
        send_mail(
            subject="Confirmation de votre adresse email",
            message=f"Bonjour {instance.username},\n\nMerci de vous être inscrit. Cliquez sur le lien suivant pour confirmer votre adresse email : {full_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )

        send_mail(
            subject="Votre candidature a été reçue !",
            message=f"Bonjour {instance.username},\n\nMerci pour votre intérêt à créer une entreprise avec nous.Votre candidature a été reçue par notre système. Nous vous contacterons dès que possible pour discuter des prochaines étapes.:",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )




from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=SocialAccount)
def sync_user_profile(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        extra_data = instance.extra_data

        user.name = extra_data.get('name', user.name)
        user.phone = extra_data.get('phone')  # Ajoutez des champs personnalisés si existants
        user.is_active = True  # Activez automatiquement
        user.save()
