from django.urls import path

from . import views
from . import cron

app_name = "lynx"

urlpatterns = [
    path("", views.index, name='index'),
    # At the moment, this one pull all active clients into a dropdown, so the path name should probably reflect that (e.g., `clients/active`). Why not just list them with the ability to search all contacts at the top?
    path('client/new',           views.ContactCreateView.as_view(), name='contact_new'),
    path('client/search',        views.contact_search,              name='contact_search'),
    path('client/<int:pk>',      views.ContactDetailView.as_view(), name='contact_show'),
    # TODO 20260517_2108 This doesn't work; remove this, and instead add buttons to update name and program memberships (or fix the form so that it works properly...)
    path('client/<int:pk>/edit', views.ContactUpdateView.as_view(), name='contact_edit'),
    path('client/filter',        views.contact_filter,              name='contact_filter'),

    path('client/<int:contact_id>/address/new', views.contact_address_add, name='contact_address_new'),
    path('client/<int:contact_id>/address/<int:pk>/edit', views.AddressUpdateView.as_view(), name='contact_address_edit'),

    path('client/<int:contact_id>/email/new', views.email_add, name='contact_email_new'),
    path('client/<int:contact_id>/email/<int:pk>/edit', views.EmailUpdateView.as_view(), name='contact_email_edit'),

    path('client/<int:contact_id>/phone_number/new', views.phone_add, name='contact_phone_new'),
    path('client/<int:contact_id>/phone_number/<int:pk>/edit', views.PhoneUpdateView.as_view(), name='contact_phone_edit'),
    path('client/<int:contact_id>/phone_number/<int:pk>/delete', views.PhoneDeleteView.as_view(), name='contact_phone_delete'),

    path('client/<int:contact_id>/emergency-contacts/new', views.emergency_contact_add, name='emergency_contact_new'),
    path('client/<int:contact_id>/emergency-contacts/<int:emergency_contact_id>/emails/new', views.email_add, name='emergency_contact_email_new'),
    path('client/<int:contact_id>/emergency-contacts/<int:emergency_contact_id>/phone_number/new', views.phone_add, name='emergency_contact_phone_new'),

    path('client/<int:contact_id>/vaccine/new', views.add_vaccination_record, name='vaccine_new'),
    path('client/<int:contact_id>/vaccine/<int:pk>/edit', views.VaccineUpdateView.as_view(), name='vaccine_edit'),
    path('client/<int:contact_id>/vaccine/<int:pk>/delete', views.VaccineDeleteView.as_view(), name='vaccine_delete'),

    path('client/<int:contact_id>/intake/new', views.intake_add, name='intake_new'),
    path('client/<int:contact_id>/intake/<int:pk>/confirm-birth-date-for-oib-program/', views.IntakeBirthDateConfirmView.as_view(), name='intake_birthdate_confirm'),

    # path('client-advanced-search', views.client_advanced_result_view, name='client_advanced_search'),

    # TODO 20260308_1955 What is the purpose of the Django admin site?
    # Even though one could use it to manage entities # (contacts, notes, service_events, etc.), but it is # mostly used for Lynx user management - but even that # is not accessible.
    # So, use it to manage entities that are rarely touched? (Was meaning to write non-client contacts, but those can be managed from `client/` as well...)

    # === CORE ============================================================ {{-
    path('core/client/<int:client_id>/authorizations', views.authorization_list, name='core_authorization_list'),
    path('core/client/<int:client_id>/authorization/<int:pk>', views.AuthorizationDetailView.as_view(), name='core_authorization_show'),
    path('core/client/<int:contact_id>/authorization/new', views.add_authorization, name='core_authorization_new'),
    path('core/client/<int:contact_id>/authorization/<int:pk>/edit', views.AuthorizationUpdateView.as_view(), name='core_authorization_edit'),
    path('core/client/<int:contact_id>/authorization/<int:pk>/delete', views.AuthorizationDeleteView.as_view(), name='core_authorization_delete'),

    path('core/client/<int:client_id>/authorization/<int:authorization_id>/progress-report/<int:pk>', views.ProgressReportDetailView.as_view(), name='core_progress_report_show'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/progress-report/new', views.add_progress_report, name='core_progress_report_new'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/progress-report/<int:pk>/edit', views.ProgressReportUpdateView.as_view(), name='core_progress_report_edit'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/progress-report/<int:pk>/delete', views.ProgressReportDeleteView.as_view(), name='core_progress_report_delete'),

    path('core/client/<int:client_id>/authorization/<int:authorization_id>/lesson-note/<int:pk>', views.LessonNoteDetailView.as_view(), name='core_lesson_note_show'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/lesson-note/new', views.add_lesson_note, name='core_lesson_note_new'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/lesson-note/<int:pk>/edit', views.LessonNoteUpdateView.as_view(), name='core_lesson_note_edit'),
    path('core/client/<int:client_id>/authorization/<int:authorization_id>/lesson-note/<int:pk>/delete', views.LessonNoteDeleteView.as_view(), name='core_lesson_note_delete'),

    path('core/client/<int:client_id>/authorization/<int:pk>/invoice', views.CoreInvoice.as_view(), name='core_invoice_show'),
    # ===================================================================== }}-

    # TODO See 20260304_2153
    # path('get-hour-validation/<int:authorization_id>/<int:billed_units>', views.get_hour_validation, name='get_hour_validation'),
    # path('get-date-validation/<int:authorization_id>/<str:note_date>', views.get_date_validation, name='get_date_validation'),

    # === REPORT ========================================================== {{-
    path('reports', views.reports, name='reports'),
    path('report/core/monthly-invoices-and-progress-reports', views.progress_result_view, name='core_monthly_print'),

    path('billing-report/', views.billing_report, name='billing_report'),
    path('sip-demographic-report/', views.sip_demographic_report, name='sip_demo_report'),
    path('sip-quarterly-demo-report/', views.sip_csf_demographic_report, name='sip_quarterly_demo_report'),
    path('sip-quarterly-service-report/', views.sip_csf_services_report, name='sip_quarterly_service_report'),
    path('sip-quarterly-report/', views.sip_quarterly_report, name='sip_quarterly_report'),
    path('intake-edit/<int:pk>', views.IntakeUpdateView.as_view(), name='intake-edit'),
    path('emergency-contact-edit/<int:pk>', views.EmergencyContactUpdateView.as_view(), name='emergency-contact-edit'),
    path('contact-confirm/<int:pk>', views.ContactDeleteView.as_view(), name='contact-delete'),
    path('document-confirm/<int:pk>/<int:client_id>', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('download/<path:path>', views.download, name='download'),
    path('manual', views.ManualView.as_view(), name='manual'),
    path('intake-note-confirm/<int:pk>/<int:client_id>', views.IntakeNoteDeleteView.as_view(), name='intake-note-delete'),
    path('intake-note-edit/<int:pk>', views.IntakeNoteUpdateView.as_view(), name='intake-note-edit'),

    # === ASSIGNMENTS (OIB programs only) ================================= {{-
    path('client/<int:contact_id>/oib/assignments/new', views.oib_assigment_add, name='oib_assignment_new'),
    path('client/<int:contact_id>/oib/assignments', views.oib_assignment_list_for_client, name='oib_assignment_for_client'),
    path('client/<int:contact_id>/oib/assignment/<int:pk>/edit', views.AssignmentUpdateView.as_view(), name='oib_assignment_edit'),
    path('client/<int:contact_id>/oib/assignment/<int:pk>/delete', views.AssignmentDeleteView.as_view(), name='oib_assignment_delete'),
    path('oib/assignments', views.oib_assignment_list, name='oib_assignment_list'),
    # ===================================================================== }}-

    # === OIB ============================================================= {{-
    # OIB service events (aka. "notes")
    path('oib/service-events/<int:oib_service_event_id>',
         views.oib_service_event_show,
         name='oib_service_event_show'
        ),
    path('oib/service-events/new',
         views.oib_service_event_form,
         name='oib_service_event_add'
        ),
    path('oib/service-events/<int:oib_service_event_id>/edit',
         views.oib_service_event_form,
         name='oib_service_event_edit'
        ),
    path('oib/service-events/<int:oib_service_event_id>/delete',
         views.oib_service_event_delete,
         name='oib_service_event_delete'
        ),
    path('oib/service-events',
         views.oib_service_event_list,
         name='oib_service_event_list'
        ),
    path('oib/service-events/<int:contact_id>/<str:program>',
         views.oib_service_events_per_client_per_program,
         name='oib_service_events_per_client_per_program'
        ),

    # "plans" (one / client / grant year / service delivery type (aka. plan type))
    path('oib/client/<int:contact_id>/plans',
         views.oib_plan_list,
         name='oib_plan_list'
        ),
    path('oib/client/<int:contact_id>/plans-with-notes',
         views.oib_plan_list_with_notes,
         name='oib_plan_list_with_notes'
        ),
    path('oib/client/<int:contact_id>/plans/<str:program>/<int:grant_year>/<int:service_delivery_type_id>',
         views.oib_plan_show,
         name='oib_plan_show'
        ),
    path('oib/client/<int:contact_id>/plans/<str:program>/<int:grant_year>/<int:service_delivery_type_id>/edit',
         views.oib_plan_edit,
         name='oib_plan_edit'
        ),

    # HTMX endpoint for dynamically loading active OIB clients in a select field
    path('htmx/oib-service-events/active-oib-clients', views.active_oib_clients, name='active_oib_clients'),
    # ===================================================================== }}-
]
