from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resources'),
    path('search/', views.search_resources, name='search_resources'),
    path('category/<str:category>/', views.resource_category, name='resource_category'),
    path('<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('new/', views.create_resource, name='create_resource'),
    path('<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
]