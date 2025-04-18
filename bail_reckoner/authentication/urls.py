from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('verify-aadhaar/', views.verify_aadhaar, name='verify_aadhaar'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]