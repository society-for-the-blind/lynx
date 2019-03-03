from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-intake/', views.add_intake, name='add_intake'),
]