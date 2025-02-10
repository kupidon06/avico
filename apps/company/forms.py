from django import forms
from .models import Subscription,Company,Payment,Domain
from django.apps import apps
from django.conf import settings

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['company', 'plan', 'start_date', 'end_date', 'active']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

   
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['subscription', 'amount', 'payment_status', 'payment_method', 'transaction_id', 'remark']
