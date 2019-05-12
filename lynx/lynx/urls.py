from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-intake/1/', views.IntakeFormView.as_view(), name='add_intake1'),
    # path('add-intake/1/', views.add_intake1, name='add_intake1'),
    path('add-intake/2/', views.add_intake2, name='add_intake2'),
    path('clients', views.ContactListView.as_view(), name='contact-list'),
    path('client/<int:pk>', views.ContactDetailView.as_view(), name='contact-detail'),

]