from django.urls import path

from . import views
from . import cron

app_name = "lynx"

urlpatterns = [
    path("", views.index, name='index'),
    # At the moment, this one pull all active clients into a dropdown, so the path name should probably reflect that (e.g., `clients/active`). Why not just list them with the ability to search all contacts at the top?
    path('clients/new',           views.ContactCreateView.as_view(), name='contact_add'),
    path('clients/search',        views.contact_search,              name='contact_search'),
    path('clients/<int:pk>',      views.ContactDetailView.as_view(), name='contact_show'),
    path('clients/<int:pk>/edit', views.ContactUpdateView.as_view(), name='contact_edit'),
    path('clients/filter',        views.contact_filter,              name='contact_filter'),

    path('clients/<int:contact_id>/address/new', views.contact_address_add, name='contact_address_add'),
    path('clients/<int:contact_id>/email/new', views.email_add, name='contact_email_add'),
    path('clients/<int:contact_id>/phone_number/new', views.phone_add, name='contact_phone_add'),

    path('clients/<int:contact_id>/emergency-contacts/new', views.emergency_contact_add, name='emergency_contact_add'),
    path('clients/<int:contact_id>/emergency-contacts/<int:emergency_contact_id>/emails/new', views.email_add, name='emergency_contact_email_add'),
    path('clients/<int:contact_id>/emergency-contacts/<int:emergency_contact_id>/phone_number/new', views.phone_add, name='emergency_contact_phone_add'),

    path('add-vaccination/<int:contact_id>/', views.add_vaccination_record, name='add_vaccination_record'),

    path('clients/<int:contact_id>/intake/new', views.intake_add, name='intake_add'),
    path('intake/<int:pk>/confirm-birth-date/', views.IntakeBirthDateConfirmView.as_view(), name='intake_birthdate_confirm'),

    path('reports', views.reports, name='reports'),

    # path('client-advanced-search', views.client_advanced_result_view, name='client_advanced_search'),

    # TODO 20260308_1955 What is the purpose of the Django admin site?
    # Even though one could use it to manage entities # (contacts, notes, service_events, etc.), but it is # mostly used for Lynx user management - but even that # is not accessible.
    # So, use it to manage entities that are rarely touched? (Was meaning to write non-client contacts, but those can be managed from `clients/` as well...)

    path('core_authorizations/<int:client_id>', views.authorization_list, name='core_authorization_list'),

    # ================================================================================================================
    path('address-edit/<int:pk>', views.AddressUpdateView.as_view(), name='address-edit'),
    path('phone-edit/<int:pk>', views.PhoneUpdateView.as_view(), name='phone-edit'),
    path('email-edit/<int:pk>', views.EmailUpdateView.as_view(), name='email-edit'),
    path('add-authorization/<int:contact_id>/', views.add_authorization, name='add_authorization'),
    # TODO See 20260304_2153
    # path('get-hour-validation/<int:authorization_id>/<int:billed_units>', views.get_hour_validation, name='get_hour_validation'),
    # path('get-date-validation/<int:authorization_id>/<str:note_date>', views.get_date_validation, name='get_date_validation'),
    path('add-progress-report/<int:authorization_id>/', views.add_progress_report, name='add_progress_report'),
    path('billing-report/', views.billing_report, name='billing_report'),
    path('sip-demographic-report/', views.sip_demographic_report, name='sip_demo_report'),
    path('sip-quarterly-demo-report/', views.sip_csf_demographic_report, name='sip_quarterly_demo_report'),
    path('sip-quarterly-service-report/', views.sip_csf_services_report, name='sip_quarterly_service_report'),
    path('sip-quarterly-report/', views.sip_quarterly_report, name='sip_quarterly_report'),
    path('authorization/<int:pk>', views.AuthorizationDetailView.as_view(), name='authorization_detail'),
    path('progress-report/<int:pk>/', views.ProgressReportDetailView.as_view(), name='progress_report_detail'),
    path('billing-review/<int:pk>/', views.BillingReviewDetailView.as_view(), name='billing_review'),
    path('intake-edit/<int:pk>', views.IntakeUpdateView.as_view(), name='intake-edit'),
    path('progress-report-edit/<int:pk>', views.ProgressReportUpdateView.as_view(), name='progresss-report-edit'),
    path('emergency-contact-edit/<int:pk>', views.EmergencyContactUpdateView.as_view(), name='emergency-contact-edit'),
    path('authorization-edit/<int:pk>', views.AuthorizationUpdateView.as_view(), name='authorization-edit'),
    path('vaccine-edit/<int:pk>', views.VaccineUpdateView.as_view(), name='vaccine-edit'),
    path('progress-report-confirm/<int:pk>/<int:auth_id>', views.ProgressReportDeleteView.as_view(), name='pr-delete'),
    path('authorization-confirm/<int:pk>/<int:client_id>', views.AuthorizationDeleteView.as_view(), name='auth-delete'),
    path('phone-confirm/<int:pk>/<int:client_id>', views.PhoneDeleteView.as_view(), name='phone-delete'),
    path('vaccine-confirm/<int:pk>/<int:client_id>', views.VaccineDeleteView.as_view(), name='vaccine-delete'),
    path('contact-confirm/<int:pk>', views.ContactDeleteView.as_view(), name='contact-delete'),
    path('document-confirm/<int:pk>/<int:client_id>', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('report-search', views.progress_result_view, name='report_search'),
    path('download/<path:path>', views.download, name='download'),
    path('manual', views.ManualView.as_view(), name='manual'),
    path('email', views.email_update, name='email'),
    path('intake-note-confirm/<int:pk>/<int:client_id>', views.IntakeNoteDeleteView.as_view(), name='intake-note-delete'),
    path('lesson-note-confirm/<int:pk>/<int:auth_id>', views.LessonNoteDeleteView.as_view(), name='ln-delete'),
    path('add-lesson-note/<int:authorization_id>/', views.add_lesson_note, name='add_lesson_note'),
    path('lesson-note/<int:pk>/', views.LessonNoteDetailView.as_view(), name='lesson_note'),
    path('lesson-note-edit/<int:pk>', views.LessonNoteUpdateView.as_view(), name='lesson-note-edit'),
    path('intake-note-edit/<int:pk>', views.IntakeNoteUpdateView.as_view(), name='intake-note-edit'),

    ###############
    # ASSIGNMENTS #
    ###############
    path('oib-assignments/<int:contact_id>', views.oib_assignment_list_for_client, name='oib_assignment_for_client'),
    path('clients/<int:contact_id>/oib-assigments/new', views.oib_assigment_add, name='oib_assignment_add'),
    path('assignment-edit/<int:pk>', views.AssignmentUpdateView.as_view(), name='assignment-edit'),
    path('assignment-confirm/<int:pk>/<int:client_id>', views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    path('oib-assignments', views.oib_assignment_list, name='oib_assignment_list'),

    ################
    # OIB RE-WRITE #
    ################
    
    # OIB service events (aka. "notes")
    path('oib-service-events/<int:oib_service_event_id>',
         views.oib_service_event_show,
         name='oib_service_event_show'
        ),
    path('oib-service-events/new',
         views.oib_service_event_form,
         name='oib_service_event_add'
        ),
    path('oib-service-events/<int:oib_service_event_id>/edit',
         views.oib_service_event_form,
         name='oib_service_event_edit'
        ),
    path('oib-service-events/<int:oib_service_event_id>/delete',
         views.oib_service_event_delete,
         name='oib_service_event_delete'
        ),
    path('oib-service-events',
         views.oib_service_event_list,
         name='oib_service_event_list'
        ),
    path('oib-service-events/<int:contact_id>/<str:program>',
         views.oib_service_events_per_client_per_program,
         name='oib_service_events_per_client_per_program'
        ),

    # "plans" (one / client / grant year / service delivery type (aka. plan type))
    path('clients/<int:contact_id>/plans',
         views.oib_plan_list,
         name='oib_plan_list'
        ),
    path('clients/<int:contact_id>/plans-with-notes',
         views.oib_plan_list_with_notes,
         name='oib_plan_list_with_notes'
        ),
    path('clients/<int:contact_id>/plans/<str:program>/<int:grant_year>/<int:service_delivery_type_id>',
         views.oib_plan_show,
         name='oib_plan_show'
        ),
    path('clients/<int:contact_id>/plans/<str:program>/<int:grant_year>/<int:service_delivery_type_id>/edit',
         views.oib_plan_edit,
         name='oib_plan_edit'
        ),

    # HTMX endpoint for dynamically loading active OIB clients in a select field
    path('htmx/oib-service-events/active-oib-clients', views.active_oib_clients, name='active_oib_clients'),

]
