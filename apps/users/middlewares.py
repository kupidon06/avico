import threading

# Stockage thread-local pour le domaine du tenant
_local = threading.local()

class TenantDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.tenant_domain = request.get_host()  # Stocker le domaine
        response = self.get_response(request)
        return response

def get_current_tenant_domain():
    """Récupère le domaine du tenant depuis le thread local"""
    return getattr(_local, "tenant_domain", None)
