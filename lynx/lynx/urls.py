from django.urls import path

from . import views

app_name = "lynx"

urlpatterns = [

    # path('add-contact/', views.IntakeFormView.as_view(), name='add_intake1'),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('add-intake/', views.add_intake, name='add_intake'),
    path('clients', views.ContactListView.as_view(), name='contact-list'),
    path('client/<int:pk>', views.ContactDetailView.as_view(), name='contact-detail'),
    path('', views.index, name='index'),
]