from django.urls import path,include
from . import views
from . import html 


urlpatterns = [

    path('', views.dashboard, name="dashboard"),
    path('company/', include('apps.company.urls')),
    path('products/', include('apps.products.urls')),
    path('management/', include('apps.management.urls')),
    path('orders/', include('apps.orders.urls')),
    path('users/', include('apps.users.urls')),
    path('config/', include('apps.profile.urls')),
    
]
