from django.urls import path
from . import views
from . import html 
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500


handler404 = views.error_404
handler500 = views.error_500

urlpatterns = [
    # Index
    
   
    path('', html.index, name="home"),
    path('accounts/register/', views.register_view, name="register"),
    path('accounts/login/', views.UserLoginView.as_view(), name="login"),
    path('accounts/logout/', views.logout_view, name="logout"),
    path('accounts/password-change/', views.password_change, name='password_change'),
    path('accounts/password-change-done/', views.password_reset_done, name="password_change_done"),
    path('accounts/password-reset/', views.password_reset, name="password_reset"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name="password_reset_confirm"),
    path('accounts/password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('accounts/password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    path('accounts/lock/', views.lock, name="lock"),

    # Errors
    path('error/404/', views.error_404, name="error_404"),
    path('error/500/', views.error_500, name="error_500"),
]
