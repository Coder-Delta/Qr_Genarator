from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-invoice/', views.generate_invoice, name='generate_invoice'),
]
