from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.urls import path, include,re_path
from django_tenants.middleware.main import TenantMainMiddleware
from apps.dashboard.html import index
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [



    # Dashboard
    path('', include('apps.dashboard.tenanturls')),
    
    path('dashboard/', include('apps.dashboard.dashurls')),
    
    # Auth - JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Allauth Endpoints
    path('auth/', include('allauth.urls')),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
