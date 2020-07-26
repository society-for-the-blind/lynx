from django.urls import path

from . import views

app_name = "lynx"

urlpatterns = [
    path('clients/', views.client_list_view, name='contact_list'),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('add-authorization/<int:contact_id>/', views.add_authorization, name='add_authorization'),
    path('add-lesson-note/<int:authorization_id>/', views.add_lesson_note, name='add_lesson_note'),
    path('add-intake/<int:contact_id>/', views.add_intake, name='add_intake'),
    # path('add-contact-information/<int:contact_id>/', views.add_contact_information, name='add_contact_information'),
    path('add-emergency/<int:contact_id>/', views.add_emergency, name='add_emergency'),
    path('add-address/<int:contact_id>/', views.add_address, name='add_address'),
    path('add-email/<int:contact_id>/', views.add_email, name='add_email'),
    path('add-emergency-email/<int:emergency_contact_id>/', views.add_emergency_email, name='add_email'),
    path('add-phone/<int:contact_id>/', views.add_phone, name='add_phone'),
    path('add-emergency-phone/<int:emergency_contact_id>/', views.add_emergency_phone, name='add_phone'),
    path('add-sip-note/<int:contact_id>/', views.add_sip_note, name='add_sip_note'),
    path('add-progress-report/<int:authorization_id>/', views.add_progress_report, name='add_progress_report'),
    path('add-volunteer/', views.add_volunteer, name='add_volunteer'),
    path('billing-report/', views.billing_report, name='billing_report'),
    path('sip-demographic-report/', views.sip_demographic_report, name='sip_demo_report'),
    path('authorization/<int:pk>', views.AuthorizationDetailView.as_view(), name='authorization_detail'),
    path('client/<int:pk>', views.ContactDetailView.as_view(), name='client'),
    path('progress-report/<int:pk>/', views.ProgressReportDetailView.as_view(), name='progress_report_detail'),
    path('lesson-note/<int:pk>/', views.LessonNoteDetailView.as_view(), name='lesson_note'),
    path('billing-review/<int:pk>/', views.BillingReviewDetailView.as_view(), name='billing_review'),
    path('volunteer/<int:pk>/', views.VolunteerDetailView.as_view(), name='volunteer'),
    path('contact-edit/<int:pk>', views.ClientUpdateView.as_view(), name='contact-edit'),
    path('address-edit/<int:pk>', views.AddressUpdateView.as_view(), name='address-edit'),
    path('phone-edit/<int:pk>', views.PhoneUpdateView.as_view(), name='phone-edit'),
    path('lesson-note-edit/<int:pk>', views.LessonNoteUpdateView.as_view(), name='lesson-note-edit'),
    path('email-edit/<int:pk>', views.EmailUpdateView.as_view(), name='email-edit'),
    path('intake-edit/<int:pk>', views.IntakeUpdateView.as_view(), name='intake-edit'),
    path('intake-note-edit/<int:pk>', views.IntakeNoteUpdateView.as_view(), name='intake-note-edit'),
    path('sip-note-edit/<int:pk>', views.SipNoteUpdateView.as_view(), name='sip-note-edit'),
    path('progress-report-edit/<int:pk>', views.ProgressReportUpdateView.as_view(), name='progresss-report-edit'),
    path('emergency-contact-edit/<int:pk>', views.EmergencyContactUpdateView.as_view(), name='emergency-contact-edit'),
    path('authorization-edit/<int:pk>', views.AuthorizationUpdateView.as_view(), name='authorization-edit'),
    path('client-search', views.client_result_view, name='client_search'),
    path('report-search', views.progress_result_view, name='report_search'),
    path("", views.index, name='index')
]
