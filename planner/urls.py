from django.urls import path
from . import views

urlpatterns = [
    path('', views.visit_form, name='visit_form'),
    path('result/', views.visit_result, name='visit_result'),
]
