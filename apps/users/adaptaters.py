from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from apps.users.models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Override the default save_user method to include custom fields.
        """
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.name = data.get('name')
        user.phone = data.get('phone')
        user.role = data.get('role', 'customer')  # Valeur par défaut si aucun rôle n'est fourni
        if commit:
            user.save()
        return user


from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.forms import ValidationError

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Si l'utilisateur existe déjà, associez-le
        if sociallogin.is_existing:
            return
        
        user = sociallogin.user
        email = user.email.lower()
        
        if email:
            try:
                # Associer à un utilisateur existant
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass  # Nouvel utilisateur, laissez-le être créé

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.role = 'customer'  # Par défaut, un utilisateur Google devient "customer"
        user.save()
        return user

