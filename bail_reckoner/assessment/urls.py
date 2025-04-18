from django.urls import path
from . import views

urlpatterns = [
    path('cases/', views.case_list, name='cases'),
    path('cases/new/', views.create_case, name='create_case'),
    path('cases/<str:case_id>/', views.case_detail, name='case_detail'),
    path('cases/<str:case_id>/edit/', views.edit_case, name='edit_case'),
    path('applications/<str:application_id>/', views.application_detail, name='application_detail'),
    path('applications/<str:application_id>/edit/', views.edit_application, name='edit_application'),
    path('applications/<str:application_id>/review/', views.review_application, name='review_application'),
    path('applications/<str:application_id>/assess/', views.assess_application, name='assess_application'),
    path('applications/<str:application_id>/verify/', views.verify_blockchain, name='verify_blockchain'),
]