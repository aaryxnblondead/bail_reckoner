from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('api/chart-data/', views.chart_data, name='chart_data'),
]