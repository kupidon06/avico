from django.db import connection
from django.core.management import call_command
from django.core.exceptions import ValidationError

from .migrate import migrate_tenant
class TenantCreationMixin:
    
   
    def create_and_migrate_tenant(self, name, schema_name, domain,user):
    
        migrate_tenant.delay(schema_name,name, domain,user)
            

        
    