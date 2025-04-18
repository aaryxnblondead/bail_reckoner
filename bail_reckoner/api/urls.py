from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cases', views.CaseViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'resources', views.ResourceViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('token/', views.obtain_auth_token, name='api_token_auth'),
    path('blockchain/verify/', views.verify_document, name='api_verify_document'),
    path('ai/assess/', views.ai_assessment, name='api_ai_assessment'),
]