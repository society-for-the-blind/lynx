from django.urls import path

from . import views
from . import cron

app_name = "lynx"

urlpatterns = [
    path('clients/', views.client_result_view, name='contact_list'),
    path('volunteers/', views.volunteer_list_view, name='volunteer_list'),
    path('authorizations/<int:client_id>', views.authorization_list_view, name='auth_list'),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('add-authorization/<int:contact_id>/', views.add_authorization, name='add_authorization'),
    path('get-hour-validation/<int:authorization_id>/<int:billed_units>', views.get_hour_validation, name='get_hour_validation'),
    path('add-intake/<int:contact_id>/', views.add_intake, name='add_intake'),
    path('add-emergency/<int:contact_id>/', views.add_emergency, name='add_emergency'),
    path('add-address/<int:contact_id>/', views.add_address, name='add_address'),
    path('add-email/<int:contact_id>/', views.add_email, name='add_email'),
    path('add-emergency-email/<int:emergency_contact_id>/', views.add_emergency_email, name='add_email'),
    path('add-phone/<int:contact_id>/', views.add_phone, name='add_phone'),
    path('add-emergency-phone/<int:emergency_contact_id>/', views.add_emergency_phone, name='add_phone'),
    path('add-vaccination/<int:contact_id>/', views.add_vaccination_record, name='add_vaccination_record'),
    path('add-volunteer-hours/', views.add_volunteer_hours, name='add_volunteer_hours'),
    path('add-progress-report/<int:authorization_id>/', views.add_progress_report, name='add_progress_report'),
    path('add-volunteer/', views.add_volunteer, name='add_volunteer'),
    path('billing-report/', views.billing_report, name='billing_report'),
    path('volunteer-report/', views.volunteers_report_month, name='volunteer-report-by-month'),
    path('volunteer-report/by-program', views.volunteers_report_program, name='volunteer-report-by-program'),
    path('sip-demographic-report/', views.sip_demographic_report, name='sip_demo_report'),
    path('sip-quarterly-demo-report/', views.sip_csf_demographic_report, name='sip_quarterly_demo_report'),
    path('sip-quarterly-service-report/', views.sip_csf_services_report, name='sip_quarterly_service_report'),
    path('sip-quarterly-report/', views.sip_quarterly_report, name='sip_quarterly_report'),
    path('authorization/<int:pk>', views.AuthorizationDetailView.as_view(), name='authorization_detail'),
    path('client/<int:pk>', views.ContactDetailView.as_view(), name='client'),
    path('progress-report/<int:pk>/', views.ProgressReportDetailView.as_view(), name='progress_report_detail'),
    path('billing-review/<int:pk>/', views.BillingReviewDetailView.as_view(), name='billing_review'),
    path('volunteer/<int:pk>/', views.VolunteerDetailView.as_view(), name='volunteer'),
    path('contact-edit/<int:pk>', views.ClientUpdateView.as_view(), name='contact-edit'),
    path('address-edit/<int:pk>', views.AddressUpdateView.as_view(), name='address-edit'),
    path('phone-edit/<int:pk>', views.PhoneUpdateView.as_view(), name='phone-edit'),
    path('email-edit/<int:pk>', views.EmailUpdateView.as_view(), name='email-edit'),
    path('intake-edit/<int:pk>', views.IntakeUpdateView.as_view(), name='intake-edit'),
    path('progress-report-edit/<int:pk>', views.ProgressReportUpdateView.as_view(), name='progresss-report-edit'),
    path('emergency-contact-edit/<int:pk>', views.EmergencyContactUpdateView.as_view(), name='emergency-contact-edit'),
    path('authorization-edit/<int:pk>', views.AuthorizationUpdateView.as_view(), name='authorization-edit'),
    path('volunteer-hour-edit/<int:pk>', views.VolunteerHourUpdateView.as_view(), name='volunteer-edit'),
    path('vaccine-edit/<int:pk>', views.VaccineUpdateView.as_view(), name='vaccine-edit'),
    path('progress-report-confirm/<int:pk>/<int:auth_id>', views.ProgressReportDeleteView.as_view(), name='pr-delete'),
    path('authorization-confirm/<int:pk>/<int:client_id>', views.AuthorizationDeleteView.as_view(), name='auth-delete'),
    path('phone-confirm/<int:pk>/<int:client_id>', views.PhoneDeleteView.as_view(), name='phone-delete'),
    path('vaccine-confirm/<int:pk>/<int:client_id>', views.VaccineDeleteView.as_view(), name='vaccine-delete'),
    path('contact-confirm/<int:pk>', views.ContactDeleteView.as_view(), name='contact-delete'),
    path('volunteer-hour-confirm/<int:pk>', views.VolunteerHourDeleteView.as_view(), name='contact-delete'),
    path('document-confirm/<int:pk>/<int:client_id>', views.DocumentDeleteView.as_view(), name='document-delete'),
    path('client-search', views.client_result_view, name='client_search'),
    path('client-advanced-search', views.client_advanced_result_view, name='client_advanced_search'),
    path('report-search', views.progress_result_view, name='report_search'),
    path('search', views.contact_list, name='searcher'),
    path('download/<path:path>', views.download, name='download'),
    path('manual', views.ManualView.as_view(), name='manual'),
    path('email', views.email_update, name='email'),
    path('reports/', views.reports, name='reports'),
    path('intake-note-confirm/<int:pk>/<int:client_id>', views.IntakeNoteDeleteView.as_view(), name='intake-note-delete'),
    path('lesson-note-confirm/<int:pk>/<int:auth_id>', views.LessonNoteDeleteView.as_view(), name='ln-delete'),
    path('add-lesson-note/<int:authorization_id>/', views.add_lesson_note, name='add_lesson_note'),
    path('get-date-validation/<int:authorization_id>/<str:note_date>', views.get_date_validation, name='get_date_validation'),
    path('lesson-note/<int:pk>/', views.LessonNoteDetailView.as_view(), name='lesson_note'),
    path('lesson-note-edit/<int:pk>', views.LessonNoteUpdateView.as_view(), name='lesson-note-edit'),
    path('intake-note-edit/<int:pk>', views.IntakeNoteUpdateView.as_view(), name='intake-note-edit'),

    ###############
    # SIP PLANS   #
    ###############
    path('sipplans/<int:client_id>',       views.plan_list_view,           name='sip_plan_list'   ),
    path('add-sip-plan/<int:contact_id>/', views.add_plan,                 name='sip_plan_add'    ),
    path('sip-plan/<int:pk>',              views.PlanDetailView.as_view(), name='sip_plan_detail' ),
    path('sip-plan-edit/<int:pk>',         views.PlanUpdateView.as_view(), name='sip_plan_edit'   ),
    # TODO Why is the `client_id` parameter needed? The pk should be enough, doesn't it?
    path('sip-plan-delete/<int:pk>/<int:client_id>', views.PlanDeleteView.as_view(), name='sip_plan_delete' ),

    ###############
    # 18-54 PLANS #
    ###############
    path('sip1854plans/<int:client_id>',       views.plan_list_view,           name='sip1854_plan_list'   ),
    path('add-sip1854-plan/<int:contact_id>/', views.add_plan,                 name='sip1854_plan_add'    ),
    path('sip1854-plan/<int:pk>',              views.PlanDetailView.as_view(), name='sip1854_plan_detail' ),
    path('sip1854-plan-edit/<int:pk>',         views.PlanUpdateView.as_view(), name='sip1854_plan_edit'   ),
    # TODO Why is the `client_id` parameter needed? The pk should be enough, doesn't it?
    path('sip1854-plan-delete/<int:pk>/<int:client_id>', views.PlanDeleteView.as_view(), name='sip1854_plan_delete' ),

    ###############
    # SIP NOTES   #
    ###############
    path('sipnotes/<int:client_id>',       views.plan_note_list_view,          name='sip_note_list'     ),
    path('add-sip-note/<int:contact_id>/', views.add_plan_note,                name='sip_note_add'      ),
    path('add-sip-note-bulk/',             views.add_sip_note_bulk,            name='sip_note_bulk_add' ),
    path('sip-note-edit/<int:pk>',         views.PlanNoteUpdateView.as_view(), name='sip_note_edit'     ),
    # TODO Why is the `client_id` parameter needed? The pk should be enough, doesn't it?
    path('sip-note-delete/<int:pk>',  views.PlanNoteDeleteView.as_view(), name='sip_note_delete' ),

    #################
    # 18-54 NOTES   #
    #################
    path('sip1854notes/<int:client_id>',       views.plan_note_list_view,   name='sip1854_note_list'     ),
    path('add-sip1854-note/<int:contact_id>/', views.add_plan_note,         name='sip1854_note_add'      ),
    path('add-sip1854-note-bulk/',             views.add_sip1854_note_bulk, name='sip1854_note_bulk_add' ),
    path('sip1854-note-edit/<int:pk>',         views.PlanNoteUpdateView.as_view(), name='sip1854_note_edit' ),
    # TODO Why is the `client_id` parameter needed? The pk should be enough, doesn't it?
    path('sip1854-note-delete/<int:pk>',  views.PlanNoteDeleteView.as_view(),  name='sip1854_note_delete' ),

    ###############
    # ASSIGNMENTS #
    ###############
    path('assignments/<int:contact_id>', views.assignment_detail, name='assignment'),
    path('add-assignment/<int:contact_id>', views.add_assignments, name='add_assignment'),
    path('assignment-edit/<int:pk>', views.AssignmentUpdateView.as_view(), name='assignment-edit'),
    path('assignment-confirm/<int:pk>/<int:client_id>', views.AssignmentDeleteView.as_view(), name='assignment-delete'),
    # TODO This should be named `assignments`
    path('instructors/', views.assignment_advanced_result_view, name='instructors'),
    # --- END ASSGNMENTS ---

    path("", views.index, name='index')
]
