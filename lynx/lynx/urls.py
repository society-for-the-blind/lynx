from django.urls import path

from . import create_views, delete_views, edit_views, report_views, views

app_name = "lynx"

urlpatterns = [
    # Addresses
    path('address-edit/<int:pk>', edit_views.AddressUpdateView.as_view(), name='address-edit'),
    path('add-address/<int:contact_id>/', create_views.add_address, name='add_address'),

    # Assignment
    path('instructor/<int:pk>', views.InstructorDetailView.as_view(), name='instructor'),
    path('instructors/', views.assignment_advanced_result_view, name='instructors'),
    path('assignment-confirm/<int:pk>/<int:client_id>', delete_views.AssignmentDeleteView.as_view(),
         name='assignment-delete'),
    path('assignment-edit/<int:pk>', edit_views.AssignmentUpdateView.as_view(), name='assignment-edit'),
    path('assignments/<int:contact_id>', views.assignment_detail, name='assignment'),
    path('add-assignment/<int:contact_id>', create_views.add_assignments, name='add_assignment'),

    # Authorizations
    path('authorization-confirm/<int:pk>/<int:client_id>', delete_views.AuthorizationDeleteView.as_view(),
         name='auth-delete'),
    path('authorization-edit/<int:pk>', edit_views.AuthorizationUpdateView.as_view(), name='authorization-edit'),
    path('authorization/<int:pk>', views.AuthorizationDetailView.as_view(), name='authorization_detail'),
    path('add-authorization/<int:contact_id>/', create_views.add_authorization, name='add_authorization'),
    path('authorizations/<int:client_id>', views.authorization_list_view, name='auth_list'),

    # Contact, sometimes called client
    path('contact-confirm/<int:pk>', delete_views.ContactDeleteView.as_view(), name='contact-delete'),
    path('contact-edit/<int:pk>', edit_views.ClientUpdateView.as_view(), name='contact-edit'),
    path('client/<int:pk>', views.ContactDetailView.as_view(), name='client'),
    path('add-contact/', create_views.add_contact, name='add_contact'),
    path('clients/', views.client_result_view, name='contact_list'),

    # Document
    path('download/<path:path>', views.download, name='download'),
    path('document-confirm/<int:pk>/<int:client_id>', delete_views.DocumentDeleteView.as_view(),
         name='document-delete'),

    # Email
    path('email', views.email_update, name='email'),
    path('email-edit/<int:pk>', edit_views.EmailUpdateView.as_view(), name='email-edit'),
    path('add-email/<int:contact_id>/', create_views.add_email, name='add_email'),
    path('add-emergency-email/<int:emergency_contact_id>/', create_views.add_emergency_email, name='add_email'),

    # Emergency Contact
    path('emergency-contact-edit/<int:pk>', edit_views.EmergencyContactUpdateView.as_view(), name='emergency-contact-edit'),
    path('add-emergency/<int:contact_id>/', create_views.add_emergency, name='add_emergency'),

    # Intake
    path('intake-edit/<int:pk>', edit_views.IntakeUpdateView.as_view(), name='intake-edit'),
    path('add-intake/<int:contact_id>/', create_views.add_intake, name='add_intake'),

    # Intake Notes
    path('intake-note-confirm/<int:pk>/<int:client_id>', delete_views.IntakeNoteDeleteView.as_view(),
         name='intake-note-delete'),
    path('intake-note-edit/<int:pk>', edit_views.IntakeNoteUpdateView.as_view(), name='intake-note-edit'),

    # Javascript calls
    path('get-hour-validation/<int:authorization_id>/<int:billed_units>', views.get_hour_validation,
         name='get_hour_validation'),
    path('get-date-validation/<int:authorization_id>/<str:note_date>', views.get_date_validation,
         name='get_date_validation'),

    # Lesson Notes
    path('lesson-note-confirm/<int:pk>/<int:auth_id>', delete_views.LessonNoteDeleteView.as_view(), name='ln-delete'),
    path('lesson-note-edit/<int:pk>', edit_views.LessonNoteUpdateView.as_view(), name='lesson-note-edit'),
    path('lesson-note/<int:pk>/', views.LessonNoteDetailView.as_view(), name='lesson_note'),
    path('add-lesson-note/<int:authorization_id>/', create_views.add_lesson_note, name='add_lesson_note'),

    # Phone Numbers
    path('phone-confirm/<int:pk>/<int:client_id>', delete_views.PhoneDeleteView.as_view(), name='phone-delete'),
    path('phone-edit/<int:pk>', edit_views.PhoneUpdateView.as_view(), name='phone-edit'),
    path('add-phone/<int:contact_id>/', create_views.add_phone, name='add_phone'),
    path('add-emergency-phone/<int:emergency_contact_id>/', create_views.add_emergency_phone, name='add_phone'),

    # Progress Reports
    path('progress-report-confirm/<int:pk>/<int:auth_id>', delete_views.ProgressReportDeleteView.as_view(),
         name='pr-delete'),
    path('progress-report-edit/<int:pk>', edit_views.ProgressReportUpdateView.as_view(), name='progress-report-edit'),
    path('progress-report/<int:pk>/', views.ProgressReportDetailView.as_view(), name='progress_report_detail'),
    path('add-progress-report/<int:authorization_id>/', create_views.add_progress_report, name='add_progress_report'),

    # Reports
    path('billing-review/<int:pk>/', views.BillingReviewDetailView.as_view(), name='billing_review'),
    path('sip-demographic-report/', report_views.sip_demographic_report, name='sip_demo_report'),
    path('sip-quarterly-demo-report/', report_views.sip_csf_demographic_report, name='sip_quarterly_demo_report'),
    path('sip-quarterly-service-report/', report_views.sip_csf_services_report, name='sip_quarterly_service_report'),
    path('sip-quarterly-report/', report_views.sip_quarterly_report, name='sip_quarterly_report'),
    path('billing-report/', report_views.billing_report, name='billing_report'),
    path('volunteer-report/', report_views.volunteers_report_month, name='volunteer-report-by-month'),
    path('volunteer-report/by-program', report_views.volunteers_report_program, name='volunteer-report-by-program'),

    # Searches
    path('client-search', views.client_result_view, name='client_search'),
    path('client-advanced-search', views.client_advanced_result_view, name='client_advanced_search'),
    path('report-search', views.progress_result_view, name='report_search'),
    path('search', views.contact_list, name='searcher'),

    # Sidebar
    path('reports/', views.reports, name='reports'),
    path('manual', views.ManualView.as_view(), name='manual'),

    # SIP Notes
    path('sip-note-confirm/<int:pk>/<int:client_id>', delete_views.SipNoteDeleteView.as_view(), name='sip-note-delete'),
    path('sip-note-edit/<int:pk>', edit_views.SipNoteUpdateView.as_view(), name='sip-note-edit'),
    path('add-sip-note-bulk/', create_views.add_sip_note_bulk, name='add_sip_note_bulk'),
    path('add-sip-note/<int:contact_id>/', create_views.add_sip_note, name='add_sip_note'),
    path('sipnotes/<int:client_id>', views.sipnote_list_view, name='note_list'),

    # SIP Plans
    path('sip-plan-confirm/<int:pk>/<int:client_id>', delete_views.SipPlanDeleteView.as_view(), name='sip-plan-delete'),
    path('sip-plan-edit/<int:pk>', edit_views.SipPlanUpdateView.as_view(), name='sip-plan-edit'),
    path('sip-plan/<int:pk>', views.SipPlanDetailView.as_view(), name='sip_plan'),
    path('add-sip-plan/<int:contact_id>/', create_views.add_sip_plan, name='add_sip_plan'),
    path('get-sip-plans/', create_views.get_sip_plans, name='get_sip_plans'),
    path('sipplans/<int:client_id>', views.sipplan_list_view, name='plan_list'),

    # Vaccines
    path('vaccine-confirm/<int:pk>/<int:client_id>', delete_views.VaccineDeleteView.as_view(), name='vaccine-delete'),
    path('vaccine-edit/<int:pk>', edit_views.VaccineUpdateView.as_view(), name='vaccine-edit'),
    path('add-vaccination/<int:contact_id>/', create_views.add_vaccination_record, name='add_vaccination_record'),

    # Volunteer
    path('volunteer-hour-confirm/<int:pk>', delete_views.VolunteerHourDeleteView.as_view(), name='contact-delete'),
    path('volunteer-hour-edit/<int:pk>', edit_views.VolunteerHourUpdateView.as_view(), name='volunteer-edit'),
    path('volunteer/<int:pk>/', views.VolunteerDetailView.as_view(), name='volunteer'),
    path('add-volunteer/', create_views.add_volunteer, name='add_volunteer'),
    path('add-volunteer-hours/', create_views.add_volunteer_hours, name='add_volunteer_hours'),
    path('volunteers/', views.volunteer_list_view, name='volunteer_list'),

    path("", views.index, name='index')
]
