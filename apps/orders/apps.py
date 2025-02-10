from django.apps import AppConfig

class OrdersConfig(AppConfig):
    name = 'apps.orders'

    def ready(self):
        # Importer les signaux
        import apps.orders.signals
