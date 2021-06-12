from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.views.generic import DetailView, ListView, FormView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.db.models import Value as V
from django.db.models.functions import Concat, Replace, Lower
from django.db import connection
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import send_mail

import os
import csv
from datetime import datetime, timedelta
import logging
import smtplib
import ssl

from .models import Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Volunteer, SipPlan, OutsideAgency, ContactInfoView, UNITS, Document
from .forms import ContactForm, IntakeForm, IntakeNoteForm, EmergencyForm, AddressForm, EmailForm, PhoneForm, \
    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm, BillingReportForm, SipDemographicReportForm, \
    VolunteerForm, SipCSFReportForm, SipPlanForm, SipNoteBulkForm, DocumentForm, VolunteerHoursForm, VolunteerReportForm
from .filters import ContactFilter

logger = logging.getLogger(__name__)

from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template


def address_changes(self):
    date = datetime.today() - timedelta(days=7)

    with connection.cursor() as cursor:
        cursor.execute("""SELECT CONCAT(client.first_name, ' ', client.last_name) as client_name,
                       CONCAT(au.first_name, ' ', au.last_name) as user_name,
                       CONCAT(his.address_one, ' ', his.suite) as address_one,
                       address_two,
                       CONCAT(his.city, ' ', his.state, ', ', his.zip_code) as city,
                       history_type, history_date, his.id
                FROM lynx_historicaladdress his
                JOIN lynx_contact client on his.contact_id = client.id
                JOIN auth_user au on his.history_user_id = au.id
                WHERE history_date > '%s' 
                  and (his.id,history_date) in (select hist.id, max(hist.history_date) 
                  from lynx_historicaladdress hist group by hist.id);""" % (date))
        change_set = dictfetchall(cursor)

    template = get_template('lynx/email_change_address.html')
    context = {'change_set': change_set}
    content = template.render(context)
    username = settings.EMAIL_HOST_USER

    subject = "Address Changes"

    msg = EmailMessage(subject, content, username, to=['mjtolentino247@gmail.com', ])
    msg.send()

    # send_mail("Address Changes",
    #           message,
    #           username,
    #           ['mjtolentino247@gmail.com'],
    #           # ['jhuynh@societyfortheblind.org '],
    #           fail_silently=False,
    #           )
    #
    return HttpResponse('Mail successfully sent')

@login_required
def index(request):
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return render(request, 'lynx/index.html', context)


@login_required
def reports(request):
    context = {
        "message": "All Lynx Reports"
    }
    return render(request, 'lynx/reports.html', context)


@login_required
def client_list_view(request):
    clients = Contact.objects.filter(active=1).order_by(Lower('last_name'), Lower('first_name'))
    return render(request, 'lynx/contact_list.html', {'clients': clients})


@login_required
def volunteer_list_view(request):
    volunteers = Contact.objects.filter(volunteer_check=1).order_by(Lower('last_name'), Lower('first_name'))
    return render(request, 'lynx/volunteer_list.html', {'volunteers': volunteers})


@login_required
def add_contact(request):
    form = ContactForm()
    address_form = AddressForm()
    phone_form = PhoneForm()
    email_form = EmailForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        address_form = AddressForm(request.POST)
        phone_form = PhoneForm(request.POST)
        email_form = EmailForm(request.POST)
        if address_form.is_valid() & phone_form.is_valid() & email_form.is_valid() & form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.save()
            contact_id = form.pk
            address_form = address_form.save(commit=False)
            phone_form = phone_form.save(commit=False)
            email_form = email_form.save(commit=False)
            if hasattr(address_form, 'address_one'):
                if address_form.address_one is not None:
                    address_form.contact_id = contact_id
                    address_form.user_id = request.user.id
                    address_form.save()
            if hasattr(phone_form, 'phone'):
                if phone_form.phone is not None:
                    phone_form.contact_id = contact_id
                    phone_form.user_id = request.user.id
                    phone_form.active = True
                    phone_form.save()
            if hasattr(email_form, 'email'):
                if email_form.email is not None:
                    email_form.contact_id = contact_id
                    email_form.user_id = request.user.id
                    email_form.active = True
                    email_form.save()
            return HttpResponseRedirect(reverse('lynx:add_emergency', args=(contact_id,)))
            # return HttpResponseRedirect(reverse('lynx:add_intake', args=(contact_id,)))
    return render(request, 'lynx/add_contact.html', {'address_form': address_form, 'phone_form': phone_form,
                                                     'email_form': email_form, 'form': form})


@login_required
def add_intake(request, contact_id):
    form = IntakeForm()
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_intake.html', {'form': form})


@login_required
def add_sip_note(request, contact_id):
    contact = {'contact_id': contact_id}
    form = SipNoteForm(**contact)
    # form = SipNoteForm(request, contact_id=contact_id)
    if request.method == 'POST':
        form = SipNoteForm(request.POST, contact_id=contact_id)

        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            note_date = form.note_date
            note_month = note_date.month
            note_year = note_date.year
            quarter = get_quarter(note_month)
            if quarter == 1:
                fiscal_year = get_fiscal_year(note_year)
            else:
                f_year = note_year - 1
                fiscal_year = get_fiscal_year(f_year)
            form.quarter = quarter
            form.fiscal_year = fiscal_year
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_sip_note.html', {'form': form, 'contact_id': contact_id})


@login_required
def add_sip_plan(request, contact_id):
    form = SipPlanForm()
    if request.method == 'POST':
        form = SipPlanForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.plan_name = request.POST.get('start_date_month') + '/' + request.POST.get('start_date_day') + '/' \
                             + request.POST.get('start_date_year') + ' - ' + request.POST.get('plan_type') + ' - ' \
                             + request.POST.get('instructor')
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_sip_plan.html', {'form': form})


@login_required
def add_sip_note_bulk(request):
    form = SipNoteBulkForm()
    client_list = Contact.objects.filter(sip_client=1).order_by(Lower('last_name'))
    range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if request.method == 'POST':
        form = SipNoteBulkForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)

            note_date = form.note_date
            note_month = note_date.month
            note_year = note_date.year
            quarter = get_quarter(note_month)
            if quarter == 1:
                fiscal_year = get_fiscal_year(note_year)
            else:
                f_year = note_year - 1
                fiscal_year = get_fiscal_year(f_year)

            form.quarter = quarter
            form.fiscal_year = fiscal_year
            form.contact_id = request.POST.get('client_0')
            form.sip_plan_id = request.POST.get('plan_0')
            form.user_id = request.user.id
            form.save()
            for i in range:
                form.pk = None
                client_str = "client_" + str(i)
                plan_str = "plan_" + str(i)
                if len(request.POST.get(client_str)) > 0:
                    form.contact_id = request.POST.get(client_str)
                    form.sip_plan_id = request.POST.get(plan_str)
                    form.quarter = quarter
                    form.fiscal_year = fiscal_year
                    form.user_id = request.user.id
                    form.save()
                else:
                    continue
        return HttpResponseRedirect(reverse('lynx:contact_list'))
    return render(request, 'lynx/add_sip_note_bulk.html', {'form': form, 'client_list': client_list, 'range': range})


def get_sip_plans(request):
    contact_id = request.GET.get('client_id')
    plans = SipPlan.objects.filter(contact_id=contact_id)
    return render(request, 'lynx/sip_plan_list_options.html', {'plans': plans})


@login_required
def add_emergency(request, contact_id):
    form = EmergencyForm()
    phone_form = PhoneForm()
    email_form = EmailForm()
    if request.method == 'POST':
        phone_form = PhoneForm(request.POST)
        email_form = EmailForm(request.POST)
        form = EmergencyForm(request.POST)
        if phone_form.is_valid() & email_form.is_valid() & form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            emergency_contact_id = form.pk
            if phone_form.data['phone']:
                if phone_form.data['phone'] is not None:
                    phone_form = phone_form.save(commit=False)
                    phone_form.active = True
                    phone_form.user_id = request.user.id
                    phone_form.emergency_contact_id = emergency_contact_id
                    phone_form.save()
            if email_form.data['email']:
                if email_form.data['email'] is not None:
                    email_form = email_form.save(commit=False)
                    email_form.active = True
                    email_form.user_id = request.user.id
                    email_form.emergency_contact_id = emergency_contact_id
                    email_form.save()

            return HttpResponseRedirect(reverse('lynx:add_intake', args=(contact_id,)))
            # return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_emergency.html',
                  {'phone_form': phone_form, 'email_form': email_form, 'form': form})


@login_required
def add_address(request, contact_id):
    form = AddressForm()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_address.html', {'form': form})


@login_required
def add_email(request, contact_id):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_email.html', {'form': form})


@login_required
def add_emergency_email(request, emergency_contact_id):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.emergency_contact_id = emergency_contact_id
            form.active = 1
            form.user_id = request.user.id
            form.save()
            emergency = EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_email.html', {'form': form})


@login_required
def add_phone(request, contact_id):
    form = PhoneForm()
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_emergency_phone(request, emergency_contact_id):
    form = PhoneForm()
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.emergency_contact_id = emergency_contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            emergency = EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_authorization(request, contact_id):
    form = AuthorizationForm()
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_authorization.html', {'form': form})


@login_required
def add_progress_report(request, authorization_id):
    full_name = request.user.first_name + ' ' + request.user.last_name
    current_time = datetime.now()
    current_month = current_time.month
    current_year = current_time.year
    form = ProgressReportForm(initial={'instructor': full_name, 'month': current_month, 'year': current_year})
    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(authorization_id,)))
    return render(request, 'lynx/add_progress_report.html', {'form': form})


@login_required
def add_volunteer(request):
    form = VolunteerForm()
    contact_form = ContactForm()
    address_form = AddressForm()
    phone_form = PhoneForm()
    email_form = EmailForm()
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        contact_form = ContactForm(request.POST)
        address_form = AddressForm(request.POST)
        phone_form = PhoneForm(request.POST)
        email_form = EmailForm(request.POST)
        if address_form.is_valid() & phone_form.is_valid() & email_form.is_valid() & form.is_valid() & contact_form.is_valid():
            contact_form = contact_form.save()
            contact_id = contact_form.pk
            form = form.save(commit=False)
            form.contact_id = contact_id
            volunteer_id = form.pk
            form.user_id = request.user.id
            form.save()
            if address_form['address_one']:
                address_form = address_form.save(commit=False)
                address_form.contact_id = contact_id
                address_form.user_id = request.user.id
                address_form.save()
            if phone_form.phone:
                phone_form = phone_form.save(commit=False)
                phone_form.contact_id = contact_id
                phone_form.user_id = request.user.id
                phone_form.save()
            if email_form.email:
                email_form = email_form.save(commit=False)
                email_form.contact_id = contact_id
                email_form.user_id = request.user.id
                email_form.save()
            return HttpResponseRedirect(reverse('lynx:volunteer_detail', args=(volunteer_id,)))
    return render(request, 'lynx/add_volunteer.html', {'address_form': address_form, 'phone_form': phone_form,
                                                       'email_form': email_form, 'form': form,
                                                       'contact_form': contact_form})


@login_required
def add_volunteer_hours(request):
    form = VolunteerHoursForm()
    if request.method == 'POST':
        form = VolunteerHoursForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            contact_id = form.contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:volunteer', args=(contact_id,)))
    return render(request, 'lynx/add_volunteer_hours.html', {'form': form})


@login_required
def add_lesson_note(request, authorization_id):
    form = LessonNoteForm()
    authorization = Authorization.objects.get(id=authorization_id)
    note_list = LessonNote.objects.filter(authorization_id=authorization_id)

    client = Contact.objects.get(id=authorization.contact_id)
    if authorization.authorization_type == 'Hours':
        auth_type = 'individual'
    else:
        auth_type = 'group'
    if request.method == 'POST':
        form = LessonNoteForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            # form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(authorization_id,)))
    return render(request, 'lynx/add_lesson_note.html', {'form': form, 'client': client, 'auth_type': auth_type,
                                                         'authorization_id': authorization_id})


def get_hour_validation(request): #check if they are entering more hours then allowed on authorization
    authorization_id = request.GET.get('authorization_id')
    billed_units = request.GET.get('billed_units')
    authorization = Authorization.objects.get(id=authorization_id)
    note_list = LessonNote.objects.filter(authorization_id=authorization_id)

    total_time = authorization.total_time
    total_units = 0
    for note in note_list:
        if note.billed_units:
            units = float(note.billed_units)
            total_units += units
    total_used = units_to_hours(total_units)
    if total_used is None or len(str(total_used)) == 0:
        total_used = 0

    note_hours = units_to_hours(float(billed_units))
    total_hours = float(total_used) + float(note_hours)

    if total_hours > float(total_time):
        return JsonResponse({"result": 'false'})
    else:
        return JsonResponse({"result": 'true'})


def get_date_validation(request): #check if they are entering a lesson note after the authorization authorization
    authorization_id = request.GET.get('authorization_id')
    note_date = request.GET.get('note_date')
    authorization = Authorization.objects.get(id=authorization_id)

    auth_date = authorization.end_date

    if note_date > auth_date:
        return JsonResponse({"result": 'false'})
    else:
        return JsonResponse({"result": 'true'})


@login_required
def volunteers_report_month(request):
    form = VolunteerReportForm()
    if request.method == 'POST':
        form = VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = Volunteer.objects.raw("""SELECT lc.id, CONCAT(lc.last_name, ', ', lc.first_name) as name, 
                                                        SUM(volunteer_hours) as hours, 
                                                        EXTRACT(MONTH FROM volunteer_date) as month, 
                                                        EXTRACT(YEAR FROM volunteer_date) as year
                                                    FROM lynx_volunteer lv
                                                    JOIN lynx_contact lc ON lv.contact_id = lc.id
                                                    WHERE lc.volunteer_check is TRUE
                                                        AND volunteer_date >= %s::date
                                                        AND volunteer_date <= %s::date
                                                    GROUP BY lc.id, 
                                                             EXTRACT(MONTH FROM volunteer_date), 
                                                             EXTRACT(YEAR FROM volunteer_date)""", [start, end])

            filename = "Volunteer Report - " + start + " - " + end
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(['Volunteer Name', 'Date', 'Hours'])

            for vol in volunteers:
                name = vol.name
                MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                          8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
                given_month = MONTHS[vol.month]
                date = given_month + ' ' + str(int(vol.year)) #there's a weird decimal for the year, casting to int first to remove it
                hours = vol.hours
                writer.writerow([name, date, hours])

            return response

    return render(request, 'lynx/volunteer_report.html', {'form': form})


@login_required
def volunteers_report_program(request):
    form = VolunteerReportForm()
    if request.method == 'POST':
        form = VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = Volunteer.objects.raw("""SELECT lc.id,
                                                        CONCAT(lc.last_name, ', ', lc.first_name) as name,
                                                        SUM(lv.volunteer_hours) as hours,
                                                        lv.volunteer_type,
                                                        EXTRACT(MONTH FROM volunteer_date) as month,
                                                        EXTRACT(YEAR FROM volunteer_date) as year
                                                    FROM lynx_volunteer lv
                                                    JOIN lynx_contact lc ON lv.contact_id = lc.id
                                                    WHERE lc.volunteer_check is TRUE
                                                        AND lv.volunteer_date >= %s::date
                                                        AND lv.volunteer_date <= %s::date
                                                    GROUP BY lc.id,
                                                        lv.volunteer_type,
                                                        EXTRACT(MONTH FROM volunteer_date),
                                                        EXTRACT(YEAR FROM volunteer_date)""", [start, end])

            filename = "Volunteer Report - " + start + " - " + end
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(['Volunteer Name', 'Date', 'Program', 'Hours'])

            for vol in volunteers:
                name = vol.name
                MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                          8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
                given_month = MONTHS[vol.month]
                date = given_month + ' ' + str(int(vol.year)) #there's a weird decimal for the year, casting to int first to remove it
                hours = vol.hours
                program = vol.volunteer_type
                writer.writerow([name, date, program, hours])

            return response

    return render(request, 'lynx/volunteer_report.html', {'form': form})


@login_required
def client_result_view(request):
    query = request.GET.get('q')
    if query:
        object_list = Contact.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name')
        ).filter(
            Q(full_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        object_list = object_list.order_by(Lower('last_name'), Lower('first_name'))
    else:
        object_list = None
    return render(request, 'lynx/client_search.html', {'object_list': object_list})


@login_required
def client_advanced_result_view(request):
    query = request.GET.get('q')
    if query:
        object_list = Contact.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name')
        ).annotate(
            phone_number=Replace('phone__phone', V('('), V(''))
        ).annotate(
            phone_number=Replace('phone_number', V(')'), V(''))
        ).annotate(
            phone_number=Replace('phone_number', V('-'), V(''))
        ).annotate(
            phone_number=Replace('phone_number', V(' '), V(''))
        ).annotate(
            zip_code=F('address__zip_code')
        ).annotate(
            county=F('address__county')
        ).annotate(
            intake_date=F('intake__intake_date')
        ).annotate(
            email_address=F('email__email')
        ).filter(
            Q(full_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(zip_code__icontains=query) |
            Q(county__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(intake_date__icontains=query) |
            Q(email_address__icontains=query)
        )

        object_list = object_list.order_by(Lower('last_name'), Lower('first_name'), 'id')
        paginator = Paginator(object_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    return render(request, 'lynx/client_advanced_search.html', {'page_obj': page_obj})


@login_required
def progress_result_view(request):
    if request.GET.get('selMonth') and request.GET.get('selYear'):
        MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                  "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        given_month = MONTHS[request.GET.get('selMonth')]
        object_list = ProgressReport.objects.filter(month=given_month).filter(
            year=request.GET.get('selYear')).order_by(Lower('authorization__contact__last_name'), 'authorization__intake_service_area__agency')

    else:
        object_list = None
        given_month = None
    return render(request, 'lynx/monthly_progress_reports.html', {'object_list': object_list, 'givenMonth': given_month,
                                                                  'givenYear': request.GET.get('selYear')})


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        context['address_list'] = Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = Phone.objects.filter(contact_id=self.kwargs['pk']).order_by('created')
        context['email_list'] = Email.objects.filter(contact_id=self.kwargs['pk'])
        context['intake_list'] = Intake.objects.filter(contact_id=self.kwargs['pk'])
        context['authorization_list'] = Authorization.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['note_list'] = IntakeNote.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['sip_list'] = SipNote.objects.filter(contact_id=self.kwargs['pk']).order_by(F('note_date').desc(nulls_last=True))
        context['sip_plan_list'] = SipPlan.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['emergency_list'] = EmergencyContact.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['document_list'] = Document.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['form'] = IntakeNoteForm
        context['upload_form'] = DocumentForm

        return context

    def post(self, request, *args, **kwargs):
        if 'note' in request.POST:
            form = IntakeNoteForm(request.POST, request.FILES)
            upload = False
        else:
            form = DocumentForm(request.POST, request.FILES)
            upload = True

        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = self.kwargs['pk']
            form.user_id = request.user.id
            if upload:
                form.description = request.FILES['document'].name
            form.save()
            action = "/lynx/client/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)


class AuthorizationDetailView(LoginRequiredMixin, DetailView):
    model = Authorization

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AuthorizationDetailView, self).get_context_data(**kwargs)
        context['report_list'] = ProgressReport.objects.filter(authorization_id=self.kwargs['pk'])
        context['note_list'] = LessonNote.objects.filter(authorization_id=self.kwargs['pk']).order_by('-date')
        notes = LessonNote.objects.filter(authorization_id=self.kwargs['pk']).values()
        authorization = Authorization.objects.filter(id=self.kwargs['pk']).values()
        total_units = 0
        total_notes = 0
        total_present = 0
        class_count = 0
        for note in notes:
            if note['attendance'] != 'Other':
                total_notes += 1
            if note['attendance'] == 'Present':
                total_present += 1
                class_count += 1
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units
            if note['billed_units']:
                note['hours'] = float(note['billed_units']) / 4
            else:
                note['hours'] = 0
        total_hours = units_to_hours(total_units)
        if authorization[0]['billing_rate'] is None:
            context['total_billed'] = 'Need to enter billing rate'
            context['rate'] = 'Need to enter billing rate'
        else:
            if authorization[0]['authorization_type'] == 'Classes':
                context['rate'] = '$' + str(authorization[0]['billing_rate']) + '/class'
                context['total_billed'] = '$' + str(round(class_count * float(authorization[0]['billing_rate']), 2))
                context['total_hours'] = class_count
            if authorization[0]['authorization_type'] == 'Hours':
                context['rate'] = '$' + str(authorization[0]['billing_rate']) + '/hour'
                context['total_billed'] = '$' + str(round(total_hours * float(authorization[0]['billing_rate']), 2))
                context['total_hours'] = total_hours
        if authorization[0]['total_time'] is None:
            context['remaining_hours'] = "Need to enter total time"
        else:
            if authorization[0]['authorization_type'] == 'Classes':
                remaining_hours = float(authorization[0]['total_time']) - class_count
                context['remaining_hours'] = remaining_hours
            if authorization[0]['authorization_type'] == 'Hours':
                remaining_hours = float(authorization[0]['total_time']) - total_hours
                context['remaining_hours'] = remaining_hours

        context['total_notes'] = total_notes
        context['total_time'] = authorization[0]['total_time']

        context['total_present'] = total_present
        context['form'] = LessonNoteForm
        return context

    def post(self, request, *args, **kwargs):
        form = LessonNoteForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = self.kwargs['pk']
            form.user_id = request.user.id
            form.save()
            action = "/lynx/authorization/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)


class ProgressReportDetailView(LoginRequiredMixin, DetailView):
    model = ProgressReport

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgressReportDetailView, self).get_context_data(**kwargs)
        MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                  "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        month_days = {'1': '-01-31', '2': '-02-28', '3': '-03-31', '4': '-04-30', '5': '-05-31', '6': '-06-30',
                      '7': '-07-31', '8': '-08-31', '9':'-09-30', '10': '-10-31', '11':'-11-30', '12': '-12-31'}

        report = ProgressReport.objects.filter(id=self.kwargs['pk']).values()
        auth_id = report[0]['authorization_id']
        month_number = report[0]['month']
        year = report[0]['year']
        if len(month_number) > 2:
            month = report[0]['month']
            month_number = MONTHS[month]
        max_date = str(year) + month_days[month_number]
        notes = LessonNote.objects.filter(authorization_id=auth_id).filter(
            date__month=month_number).filter(date__year=year).values()
        all_notes = LessonNote.objects.filter(authorization_id=auth_id).filter(date__lte=max_date).values()
        authorization = Authorization.objects.filter(id=auth_id).values()

        total_units = 0
        all_units = 0
        class_count = 0
        month_count = 0

        for note in all_notes:
            # dt = note['date']
            # dt = datetime.strptime(note['date'], '%Y-%m-%d')
            # note_month = dt.month
            # note_year = dt.year
            if note['billed_units']:
                # if (int(note_month) > int(month_number) and int(note_year) > int(year)) or int(note_year) > int(year):
                    units = float(note['billed_units'])
                    all_units += units
                    class_count += 1

        for note in notes:
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units
                month_count += 1
        if authorization[0]['authorization_type'] == 'Classes':
            context['total_hours'] = class_count  # used in total
            context['month_used'] = month_count  # used this month
            context['total_time'] = authorization[0]['total_time']
        if authorization[0]['authorization_type'] == 'Hours':
            total_hours = units_to_hours(all_units)
            context['total_hours'] = total_hours  # used in total
            month_used = units_to_hours(total_units)
            context['month_used'] = month_used  # used this month
            context['total_time'] = authorization[0]['total_time']

        if authorization[0]['total_time'] is None:
            context['remaining_hours'] = "Need to enter total time"
        else:
            if authorization[0]['authorization_type'] == 'Classes':
                remaining_hours = float(authorization[0]['total_time']) - class_count
                context['remaining_hours'] = remaining_hours
            if authorization[0]['authorization_type'] == 'Hours':
                remaining_hours = float(authorization[0]['total_time']) - total_hours
                context['remaining_hours'] = remaining_hours

        return context


class LessonNoteDetailView(LoginRequiredMixin, DetailView):
    model = LessonNote


class BillingReviewDetailView(LoginRequiredMixin, DetailView):
    model = Authorization
    template_name = 'lynx/billing_review.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BillingReviewDetailView, self).get_context_data(**kwargs)
        current_time = datetime.now()
        month = self.request.GET.get('selMonth', current_time.month)
        year = self.request.GET.get('selYear', current_time.year)
        context['month'] = month
        context['year'] = year

        auth_id = self.kwargs['pk']
        # report = ProgressReport.objects.filter(authorization_id=auth_id).values()
        notes = LessonNote.objects.filter(authorization_id=auth_id).filter(date__month=month).filter(date__year=year).order_by(
            'date').values()
        reports = ProgressReport.objects.filter(authorization_id=auth_id).values()
        month_report = ProgressReport.objects.filter(authorization_id=auth_id).filter(month=month).filter(year=year).values()[:1]
        context['month_report'] = month_report
        authorization = Authorization.objects.filter(id=auth_id).values()

        context['note_list'] = notes

        agency_id = authorization[0]['outside_agency_id']
        outside = OutsideAgency.objects.filter(id=agency_id).values()
        context['payment'] = outside[0]['contact_name'] + ' - ' + outside[0]['agency']
        contact_id = outside[0]['contact_id']
        address = Address.objects.filter(contact_id=contact_id).values()[:1]
        context['address'] = address
        phone = Phone.objects.filter(contact_id=contact_id).values()[:1]
        context['phone'] = phone

        total_units = 0
        total_notes = 0
        instructors = []

        for note in notes:
            if note['billed_units'] and note['billed_units'] is not None:
                units = float(note['billed_units'])
                total_units += units
                total_notes += 1
        for report in reports:
            if 'instructor' in report and report['instructor'] is not None:
                instructors.append(report['instructor'])
        if len(instructors) > 0 and instructors is not None:
            context['instructors'] = ", ".join(instructors)

        if authorization[0]['authorization_type'] == 'Classes':
            context['month_used'] = total_notes  # used this month
        if authorization[0]['authorization_type'] == 'Hours':
            month_used = units_to_hours(total_units)
            context['month_used'] = month_used  # used this month
        context['total_time'] = authorization[0]['total_time']

        return context


class SipPlanDetailView(LoginRequiredMixin, DetailView):
    model = SipPlan

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SipPlanDetailView, self).get_context_data(**kwargs)
        context['sip_note_list'] = SipNote.objects.filter(sip_plan_id=self.kwargs['pk']).order_by('-note_date')

        return context


class VolunteerDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'lynx/volunteer_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VolunteerDetailView, self).get_context_data(**kwargs)
        context['volunteer_list'] = Volunteer.objects.filter(contact_id=self.kwargs['pk'])
        context['address_list'] = Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = Phone.objects.filter(contact_id=self.kwargs['pk'])
        context['email_list'] = Email.objects.filter(contact_id=self.kwargs['pk'])
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'middle_name', 'last_name', 'company', 'do_not_contact', 'donor', 'deceased',
              'remove_mailing', 'active', 'contact_notes', 'sip_client', 'core_client', 'careers_plus',
              'careers_plus_youth', 'volunteer_check', 'access_news', 'other_services']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["volunteer_check"].label = "Volunteer"
        return form


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['address_one', 'address_two', 'suite', 'city', 'state', 'zip_code', 'county', 'country', 'region',
              'cross_streets', 'bad_address', 'address_notes', 'preferred_medium']
    template_name_suffix = '_edit'


class EmailUpdateView(LoginRequiredMixin, UpdateView):
    model = Email
    fields = ['email', 'email_type', 'active']
    template_name_suffix = '_edit'


class PhoneUpdateView(LoginRequiredMixin, UpdateView):
    model = Phone
    fields = ['phone', 'phone_type', 'active']
    template_name_suffix = '_edit'


class IntakeUpdateView(LoginRequiredMixin, UpdateView):
    model = Intake
    fields = ['intake_date', 'intake_type', 'age_group', 'gender', 'pronouns', 'birth_date', 'ethnicity',
              'other_ethnicity', 'income', 'first_language', 'second_language', 'other_languages', 'education',
              'living_arrangement', 'residence_type', 'performs_tasks', 'notes', 'work_history', 'veteran',
              'member_name', 'active', 'crime', 'crime_info', 'crime_other', 'parole', 'parole_info', 'crime_history',
              'previous_training', 'training_goals', 'training_preferences', 'other', 'eye_condition',
              'secondary_eye_condition', 'eye_condition_date', 'degree', 'prognosis', 'diabetes', 'diabetes_notes',
              'dialysis', 'dialysis_notes', 'hearing_loss', 'hearing_loss_notes', 'mobility', 'mobility_notes',
              'stroke', 'stroke_notes', 'seizure', 'seizure_notes', 'heart', 'heart_notes', 'arthritis',
              'arthritis_notes', 'high_bp', 'high_bp_notes', 'neuropathy', 'neuropathy_notes', 'dexterity',
              'dexterity_notes', 'migraine', 'migraine_notes', 'pain', 'pain_notes', 'asthma', 'asthma_notes', 'cancer',
              'cancer_notes', 'musculoskeletal', 'musculoskeletal_notes', 'alzheimers', 'alzheimers_notes', 'geriatric',
              'geriatric_notes', 'allergies', 'mental_health', 'substance_abuse', 'substance_abuse_notes',
              'memory_loss', 'memory_loss_notes', 'learning_disability', 'learning_disability_notes', 'other_medical',
              'medications', 'medical_notes', 'hobbies', 'employment_goals', 'hired', 'employer', 'position',
              'hire_date', 'payment_source', 'referred_by', 'communication', 'communication_notes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["other_languages"].label = "Other Language(s)"
        form.fields["other_ethnicity"].label = "Ethnicity (if other)"
        form.fields["crime"].label = "Have you been convicted of a crime?"
        form.fields[
            "crime_info"].label = "If yes, what and when did the convictions occur? What county did this conviction occur in?"
        form.fields["crime_other"].label = "Criminal Conviction Information"
        form.fields["parole"].label = "Are you on parole?"
        form.fields["parole_info"].label = "Parole Information"
        form.fields["crime_history"].label = "Additional Criminal History"
        form.fields["musculoskeletal"].label = "Musculoskeletal Disorders"
        form.fields["alzheimers"].label = "Alzheimer’s Disease/Cognitive Impairment"
        form.fields["other_medical"].label = "Other Medical Information"
        form.fields["hobbies"].label = "Hobbies/Interests"
        form.fields["high_bp"].label = "High BP"
        form.fields["geriatric"].label = "Other Major Geriatric Concerns"
        form.fields["migraine"].label = "Migraine Headache"
        form.fields["dexterity"].label = "Use of Hands, Limbs, and Fingers"
        form.fields["hire_date"].label = "Date of Hire"
        form.fields["hired"].label = "Currently Employed?"
        return form


class IntakeNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = IntakeNote
    fields = ['note']
    template_name_suffix = '_edit'


class EmergencyContactUpdateView(LoginRequiredMixin, UpdateView):
    model = EmergencyContact
    fields = ['name',  'emergency_notes', 'relationship']
    template_name_suffix = '_edit'


class LessonNoteUpdateView(LoginRequiredMixin, UpdateView):
    form_class = LessonNoteForm
    model = LessonNote
    template_name_suffix = '_edit'


class ProgressReportUpdateView(LoginRequiredMixin, UpdateView):
    model = ProgressReport
    fields = ['month', 'instructor', 'accomplishments', 'short_term_goals', 'short_term_goals_time',
              'long_term_goals', 'long_term_goals_time', 'client_behavior', 'notes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["instructor"].label = "Instructor(s)"
        form.fields["notes"].label = "Additional Comments"
        form.fields["accomplishments"].label = "Client Accomplishments"
        form.fields["client_behavior"].label = "The client's attendance, attitude, and motivation during current month"
        form.fields["short_term_goals"].label = "Remaining Short Term Objectives"
        form.fields[
            "short_term_goals_time"].label = "Estimated number of Hours needed for completion of short term objectives"
        form.fields["long_term_goals"].label = "Remaining Long Term Objectives"
        form.fields[
            "long_term_goals_time"].label = "Estimated number of Hours needed for completion of long term objectives"
        return form


class SipNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = SipNote
    fields = ['note', 'note_date', 'vision_screening', 'treatment', 'at_devices', 'at_services', 'independent_living',
              'orientation', 'communications', 'dls', 'support', 'advocacy', 'counseling', 'information', 'services',
              'retreat', 'in_home', 'seminar', 'modesto', 'group', 'community', 'class_hours', 'sip_plan', 'instructor']
    template_name_suffix = '_edit'

    def form_valid(self, form):
        post = form.save(commit=False)
        note_date = post.note_date
        # note_date = datetime.strptime(note_date, '%Y-%m-%d')
        note_month = note_date.month
        note_year = note_date.year
        quarter = get_quarter(note_month)
        if quarter == 1:
            fiscal_year = get_fiscal_year(note_year)
        else:
            f_year = note_year - 1
            fiscal_year = get_fiscal_year(f_year)
        post.quarter = quarter
        post.fiscal_year = fiscal_year
        post.save()
        action = "/lynx/client/" + str(post.contact_id)
        return HttpResponseRedirect(action)


class SipPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = SipPlan
    fields = ['note', 'at_services', 'independent_living', 'orientation', 'communications', 'dls', 'advocacy',
              'counseling', 'information', 'other_services', 'plan_name', 'living_plan_progress', 'at_outcomes',
              'community_plan_progress', 'ila_outcomes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['at_services'].label = "Assistive Technology or Services"
        form.fields['independent_living'].label = "IL/A Services"
        form.fields['orientation'].label = "O&M Skills"
        form.fields['communications'].label = "Communication skills"
        form.fields['dls'].label = "Daily Living Skills"
        form.fields['advocacy'].label = "Advocacy training"
        form.fields['information'].label = "I&R (Information & Referral)"
        form.fields['counseling'].label = "Adjustment Counseling"
        form.fields['living_plan_progress'].label = "Living Situation Outcomes"
        form.fields['community_plan_progress'].label = "Home and Community involvement Outcomes"
        form.fields['at_outcomes'].label = "AT Goal Outcomes"
        form.fields['ila_outcomes'].label = "IL/A Service Goal Outcomes"
        return form


class AuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Authorization
    fields = ['intake_service_area', 'authorization_number', 'authorization_type', 'start_date', 'end_date',
              'total_time', 'billing_rate', 'outside_agency', 'student_plan', 'notes']
    template_name_suffix = '_edit'


class VolunteerHourUpdateView(LoginRequiredMixin, UpdateView):
    model = Volunteer
    fields = ['volunteer_type', 'note', 'volunteer_date', 'volunteer_hours']
    template_name_suffix = '_edit'


class SipPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = SipPlan

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class SipNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = SipNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class IntakeNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = IntakeNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class ProgressReportDeleteView(UserPassesTestMixin, DeleteView):
    model = ProgressReport

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class AuthorizationDeleteView(UserPassesTestMixin, DeleteView):
    model = Authorization

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_detail', kwargs={'pk': client_id})


class ContactDeleteView(UserPassesTestMixin, DeleteView):
    model = Contact

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('lynx:index')


class LessonNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = LessonNote

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class VolunteerHourDeleteView(LoginRequiredMixin, DeleteView):
    model = Volunteer

    def get_success_url(self):
        return reverse_lazy('lynx:volunteer_list')


@login_required
def billing_report(request):
    form = BillingReportForm()
    if request.method == 'POST':
        form = BillingReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            if month == 'all':
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area, 
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.contact_name, ' - ', oa.agency) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_outsideagency as oa on auth.outside_agency_id = oa.id
                                        where extract(year FROM date) = '%s'
                                        order by c.last_name, c.first_name, sa.agency;""" % (year,))
                    auth_set = dictfetchall(cursor)
            else:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area, 
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.contact_name, ' - ', oa.agency) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_outsideagency as oa on auth.outside_agency_id = oa.id
                                        where extract(month FROM date) = '%s' and extract(year FROM date) = '%s'
                                        order by c.last_name, c.first_name, sa.agency;""" % (month, year))
                    auth_set = dictfetchall(cursor)

            reports = {}
            total_amount = 0
            total_hours = 0
            for report in auth_set:
                authorization_number = report['authorization_id']
                if report['billing_rate'] is None:
                    report['billing_rate'] = 0
                billing_rate = float(report['billing_rate'])
                if authorization_number in reports.keys():
                    if report['authorization_type'] == 'Hours':
                        if report['billed_units'] and report['billed_units'] is not None and reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = (float(report['billed_units']) / 4) + float(
                                reports[authorization_number]['billed_time'])
                            loop_amount = billing_rate * (float(report['billed_units']) / 4)
                            reports[authorization_number]['amount'] = (
                                        billing_rate * float(reports[authorization_number]['billed_time']))
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = float(report['billed_units']) / 4
                            loop_amount = billing_rate * (float(report['billed_units']) / 4)
                            reports[authorization_number]['amount'] = billing_rate * float(
                                reports[authorization_number]['billed_time'])
                    if report['authorization_type'] == 'Classes':
                        if report['billed_units'] and reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = 1 + float(
                                reports[authorization_number]['billed_time'])
                            reports[authorization_number]['amount'] = billing_rate + reports[authorization_number][
                                'amount']
                            loop_amount = billing_rate
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = 1
                            reports[authorization_number]['amount'] = loop_amount = billing_rate
                    # total_amount += loop_amount
                else:
                    service_area = report['service_area']
                    authorization_type = report['authorization_type']
                    outside_agency = report['outside_agency']
                    client = report['name']
                    billed_units = report['billed_units']
                    if billed_units is None:
                        billed_units = 0
                    rate = str(billing_rate)

                    billed_time = 0
                    if report['authorization_type'] == 'Hours':
                        billed_time = float(billed_units) / 4
                        amount = billing_rate * float(billed_time)
                    elif report['authorization_type'] == 'Classes':
                        if billed_units:
                            amount = billing_rate
                            billed_time = 1
                        else:
                            amount = 0
                            billed_time = 0
                    else:
                        amount = 0

                    # total_amount += amount
                    auth = {'service_area': service_area, 'authorization_number': report['authorization_number'],
                            'authorization_type': authorization_type, 'outside_agency': outside_agency, 'rate': rate,
                            'client': client, 'billed_time': billed_time, 'amount': amount}
                    reports[authorization_number] = auth

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client', 'Service Area', 'Authorization', 'Authorization Type', 'Billed Time', 'Billing Rate',
                 'Amount', 'Payment Source'])

            for key, value in reports.items():
                in_hours = '0'
                if value['billed_time']:
                    in_hours = float(value['billed_time'])
                    total_hours += in_hours
                if value['amount']:
                    total_amount += value['amount']

                writer.writerow([value['client'], value['service_area'], value['authorization_number'],
                                 value['authorization_type'], in_hours, value['rate'], value['amount'],
                                 value['outside_agency']])

            writer.writerow(['', '', '', '', total_hours, '', '$' + str(total_amount), ''])

            return response

    return render(request, 'lynx/billing_report.html', {'form': form})


@login_required
def sip_demographic_report(request):
    form = SipDemographicReportForm()
    if request.method == 'POST':
        form = SipDemographicReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            fiscal_months = ['10', '11', '12', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            fiscal_year = get_fiscal_year(year)

            first = True
            month_string = ''
            for month_no in fiscal_months:
                if month_no == month:
                    break
                else:
                    if first:
                        month_string = """SELECT client.id FROM lynx_sipnote AS sip 
                        LEFT JOIN lynx_contact AS client ON client.id = sip.contact_id 
                        WHERE fiscal_year  = '%s' and (extract(month FROM sip.note_date) = %s""" % (fiscal_year, month_no)
                        first = False
                    else:
                        month_string = month_string + ' or extract(month FROM sip.note_date) = ' + month_no

            if len(month_string) > 0:
                month_string = " and c.id not in (" + month_string + '))'

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, c.id as id, int.created as date, int.age_group, int.gender, int.ethnicity,
                    int.degree, int.eye_condition, int.eye_condition_date, int.education, int.living_arrangement, int.residence_type,
                    int.dialysis, int.stroke, int.seizure, int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma,
                    int.cancer, int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, int.memory_loss,
                    int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.referred_by, int.hearing_loss,
                    c.first_name, c.last_name, int.birth_date
                    FROM lynx_sipnote ls
                    left JOIN lynx_contact as c  on c.id = ls.contact_id
                    left JOIN lynx_intake as int  on int.contact_id = c.id
                    where c.id != 111 and extract(month FROM ls.note_date) = %s and extract(year FROM ls.note_date) = '%s' and c.sip_client is true %s
                    order by c.last_name, c.first_name;""" % (month, year, month_string))
                client_set = dictfetchall(cursor)

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client Name', 'First Name', 'Last Name', 'Age Group', 'Gender', 'Birth Date', 'Race/Ethnicity',
                 'Visual Impairment at Time of Intake', 'Major Cause of Visual Impairment',
                 'Non-Visual Impairment', 'On-Set of Significant Vision Loss', 'Highest Level of Education Completed',
                 'Type of Living Arrangement', 'Setting of Residence', 'Source of Referral'])

            client_ids = []
            for client in client_set:
                if client['id'] in client_ids:
                    continue
                impairments = ''
                client_ids.append(client['id'])
                if client['dialysis']:
                    impairments += 'Dialysis, '
                if client['stroke']:
                    impairments += 'Stroke, '
                if client['seizure']:
                    impairments += 'Seizure, '
                if client['heart']:
                    impairments += 'Cardiovascular, '
                if client['arthritis']:
                    impairments += 'Arthritis, '
                if client['high_bp']:
                    impairments += 'Hypertension, '
                if client['hearing_loss']:
                    impairments += 'Hearing Loss, '
                if client['neuropathy']:
                    impairments += 'Neuropathy, '
                if client['pain']:
                    impairments += 'Pain, '
                if client['asthma']:
                    impairments += 'Asthma, '
                if client['cancer']:
                    impairments += 'Cancer, '
                if client['musculoskeletal']:
                    impairments += 'Musculoskeletal, '
                if client['alzheimers']:
                    impairments += 'Alzheimers, '
                if client['allergies']:
                    impairments += 'Allergies, '
                if client['mental_health']:
                    impairments += 'Mental Health, '
                if client['substance_abuse']:
                    impairments += 'Substance Abuse, '
                if client['memory_loss']:
                    impairments += 'Memory Loss, '
                if client['learning_disability']:
                    impairments += 'Learning Disability, '
                if client['geriatric']:
                    impairments += 'Other Geriatric, '
                if client['dexterity']:
                    impairments += 'Mobility, '
                if client['migraine']:
                    impairments += 'Migraine, '

                if impairments:
                    impairments = impairments[:-2]

                writer.writerow(
                    [client['name'], client['first_name'], client['last_name'], client['age_group'], client['gender'],
                     client['birth_date'], client['ethnicity'], client['degree'], client['eye_condition'], impairments,
                     client['eye_condition_date'], client['education'], client['living_arrangement'],
                     client['residence_type'], client['referred_by']])

            return response

    return render(request, 'lynx/sip_demographic_report.html', {'form': form})


@login_required
def sip_quarterly_report(request):
    form = SipCSFReportForm()
    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_services_report(request):
    form = SipCSFReportForm()
    if request.method == 'POST':
        form = SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                query = """SELECT CONCAT(c.first_name, ' ', c.last_name) as name, c.id as id, ls.fiscal_year, 
                ls.vision_screening, ls.treatment, ls.at_devices, ls.at_services, ls.orientation, ls.communications, 
                ls.dls, ls.support, ls.advocacy, ls.counseling, ls.information, ls.services, addr.county, ls.note_date,
                ls.independent_living, sp.living_plan_progress, sp.community_plan_progress, sp.ila_outcomes, 
                sp.at_outcomes, ls.class_hours
                    FROM lynx_sipnote as ls
                    left JOIN lynx_contact as c on c.id = ls.contact_id
                    inner join lynx_address as addr on c.id= addr.contact_id
                    left JOIN lynx_sipplan as sp on sp.id = ls.sip_plan_id
                    where  fiscal_year = '%s' 
                    and quarter = %d 
                    and c.sip_client is true 
                    and c.id not in (SELECT contact_id FROM lynx_sipnote AS sip WHERE quarter < %d and fiscal_year = '%s')
                    order by c.last_name, c.first_name;""" % (fiscal_year, int(quarter), int(quarter), fiscal_year)
                cursor.execute(query)
                note_set = dictfetchall(cursor)

            filename = "SIP Quarterly Services Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            writer.writerow(["Program Participant", "$ Total expenditures from all sources of program funding", "Vision  Assessment (Screening/Exam/evaluation)",
                "$ Cost of Vision Assessment", "Surgical or Therapeutic Treatment", "$ Cost of Surgical/ Therapeutic Treatment",
                "$ Total expenditures from all sources of program funding", "Received AT Devices or Services B2", "$ Total for AT Devices",
                "$ Total for AT Services", "AT Goal Outcomes", "$ Total expenditures from all sources of program funding", "Received IL/A Services",
                "Received O&M", "Received Communication Skills", "Received Daily Living Skills", "Received Advocacy training",
                "Received Adjustment Counseling", "Received I&R", "Received Other Services",
                "IL/A Service Goal Outcomes", "$ Total expenditures from all sources of program funding",
                "Received Supportive Service", "# of Cases Assessed", "Living Situation Outcomes",
                "Home and Community involvement Outcomes"])

            client_ids = []
            aggregated_data = {}
            for note in note_set:
                client_id = note['id']
                if client_id not in client_ids:
                    client_ids.append(client_id)
                    aggregated_data[client_id] = {}
                    aggregated_data[client_id]['client_name'] = note['name']

                if quarter not in aggregated_data[client_id]:
                    aggregated_data[client_id][quarter] = {}
                    aggregated_data[client_id][quarter]['independent_living'] = boolean_transform(note['independent_living'])
                    aggregated_data[client_id][quarter]['vision_screening'] = boolean_transform(note['vision_screening'])
                    aggregated_data[client_id][quarter]['treatment'] = boolean_transform(note['treatment'])
                    aggregated_data[client_id][quarter]['at_devices'] = boolean_transform(note['at_devices'])
                    aggregated_data[client_id][quarter]['at_services'] = boolean_transform(note['at_services'])
                    aggregated_data[client_id][quarter]['orientation'] = boolean_transform(note['orientation'])
                    aggregated_data[client_id][quarter]['communications'] = boolean_transform(note['communications'])
                    aggregated_data[client_id][quarter]['dls'] = boolean_transform(note['dls'])
                    aggregated_data[client_id][quarter]['support'] = boolean_transform(note['support'])
                    aggregated_data[client_id][quarter]['advocacy'] = boolean_transform(note['advocacy'])
                    aggregated_data[client_id][quarter]['counseling'] = boolean_transform(note['counseling'])
                    aggregated_data[client_id][quarter]['information'] = boolean_transform(note['information'])
                    aggregated_data[client_id][quarter]['services'] = boolean_transform(note['services'])
                    aggregated_data[client_id][quarter]['living_plan_progress'] = plan_evaluation(note['living_plan_progress'])
                    aggregated_data[client_id][quarter]['community_plan_progress'] = plan_evaluation(note['community_plan_progress'])
                    aggregated_data[client_id][quarter]['at_outcomes'] = assess_evaluation(note['at_outcomes'])
                    aggregated_data[client_id][quarter]['ila_outcomes'] = assess_evaluation(note['ila_outcomes'])
                    if aggregated_data[client_id][quarter]['at_services'] == "Yes" or aggregated_data[client_id][quarter]['at_devices'] == "Yes":
                        aggregated_data[client_id][quarter]['at_devices_services'] = "Yes"
                    else:
                        aggregated_data[client_id][quarter]['at_devices_services'] = "No"
                else:
                    if boolean_transform(note['vision_screening']) == "Yes":
                        aggregated_data[client_id][quarter]['vision_screening'] = "Yes"
                    if boolean_transform(note['independent_living']) == "Yes":
                        aggregated_data[client_id][quarter]['independent_living'] = "Yes"
                    if boolean_transform(note['treatment']) == "Yes":
                        aggregated_data[client_id][quarter]['treatment'] = "Yes"
                    if boolean_transform(note['at_devices']) == "Yes" or boolean_transform(note['at_services']) == "Yes":
                        aggregated_data[client_id][quarter]['at_devices_services'] = "Yes"
                    if boolean_transform(note['orientation']) == "Yes":
                        aggregated_data[client_id][quarter]['orientation'] = "Yes"
                    if boolean_transform(note['communications']) == "Yes":
                        aggregated_data[client_id][quarter]['communications'] = "Yes"
                    if boolean_transform(note['dls']) == "Yes":
                        aggregated_data[client_id][quarter]['dls'] = "Yes"
                    if boolean_transform(note['support']) == "Yes":
                        aggregated_data[client_id][quarter]['support'] = "Yes"
                    if boolean_transform(note['advocacy']) == "Yes":
                        aggregated_data[client_id][quarter]['advocacy'] = "Yes"
                    if boolean_transform(note['counseling']) == "Yes":
                        aggregated_data[client_id][quarter]['counseling'] = "Yes"
                    if boolean_transform(note['information']) == "Yes":
                        aggregated_data[client_id][quarter]['information'] = "Yes"
                    if boolean_transform(note['services']) == "Yes":
                        aggregated_data[client_id][quarter]['services'] = "Yes"
                    if note['living_plan_progress']:
                        aggregated_data[client_id][quarter]['living_plan_progress'] = plan_evaluation(note['living_plan_progress'], aggregated_data[client_id][quarter]['living_plan_progress'])
                    if note['community_plan_progress']:
                        aggregated_data[client_id][quarter]['community_plan_progress'] = plan_evaluation(note['community_plan_progress'], aggregated_data[client_id][quarter]['community_plan_progress'])
                    if note['at_outcomes']:
                        aggregated_data[client_id][quarter]['at_outcomes'] = assess_evaluation(note['at_outcomes'], aggregated_data[client_id][quarter]['at_outcomes'])
                    if note['ila_outcomes']:
                        aggregated_data[client_id][quarter]['ila_outcomes'] = assess_evaluation(note['ila_outcomes'], aggregated_data[client_id][quarter]['ila_outcomes'])

            for key, value in aggregated_data.items():
                if '1' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['1']['at_devices_services'], "", "", value['1']['at_outcomes'], "",
                                     value['1']['independent_living'], value['1']['orientation'],
                                     value['1']['communications'], value['1']['dls'], value['1']['advocacy'],
                                     value['1']['counseling'], value['1']['information'], value['1']['services'],
                                     value['1']['ila_outcomes'], "", value['1']['support'], "",
                                     value['1']['living_plan_progress'], value['1']['community_plan_progress']])
                if '2' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['2']['at_devices_services'], "", "", value['2']['at_outcomes'], "",
                                     value['2']['independent_living'], value['2']['orientation'],
                                     value['2']['communications'], value['2']['dls'], value['2']['advocacy'],
                                     value['2']['counseling'], value['2']['information'], value['2']['services'],
                                     value['2']['ila_outcomes'], "", value['2']['support'], "",
                                     value['2']['living_plan_progress'], value['2']['community_plan_progress']])
                if '3' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['3']['at_devices_services'], "", "", value['3']['at_outcomes'], "",
                                     value['3']['independent_living'], value['3']['orientation'],
                                     value['3']['communications'], value['3']['dls'], value['3']['advocacy'],
                                     value['3']['counseling'], value['3']['information'], value['3']['services'],
                                     value['3']['ila_outcomes'], "", value['3']['support'], "",
                                     value['3']['living_plan_progress'], value['3']['community_plan_progress']])
                if '4' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['4']['at_devices_services'], "", "", value['4']['at_outcomes'], "",
                                     value['4']['independent_living'], value['4']['orientation'],
                                     value['4']['communications'], value['4']['dls'], value['4']['advocacy'],
                                     value['4']['counseling'], value['4']['information'], value['4']['services'],
                                     value['4']['ila_outcomes'], "", value['4']['support'], "",
                                     value['4']['living_plan_progress'], value['4']['community_plan_progress']])

            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_demographic_report(request):
    form = SipCSFReportForm()
    if request.method == 'POST':
        form = SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, c.id as id, int.age_group, 
                int.gender, int.ethnicity, int.degree, int.eye_condition, int.eye_condition_date, int.education, 
                int.living_arrangement, int.residence_type, addr.county, int.dialysis, int.stroke, int.seizure, 
                int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma, int.cancer, 
                int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, 
                int.memory_loss, int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.hearing_loss, 
                int.referred_by, ls.note_date, int.communication, int.other_ethnicity
                    FROM lynx_sipnote as ls
                    left JOIN lynx_contact as c on c.id = ls.contact_id
                    left JOIN lynx_intake as int on int.contact_id = c.id
                    inner join lynx_address as addr on c.id= addr.contact_id
                    where  fiscal_year = '%s' 
                    and quarter = %d 
                    and c.sip_client is true 
                    and c.id not in (SELECT contact_id FROM lynx_sipnote AS sip WHERE quarter < %d and fiscal_year = '%s')
                    order by c.last_name, c.first_name;""" % (fiscal_year, int(quarter), int(quarter), fiscal_year))

                client_set = dictfetchall(cursor)

            filename = "SIP Quarterly Demographic Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            writer.writerow(["Program Participant", "Individuals Served", "Age at Application", "Gender", "Race",
                                  "Ethnicity", "Degree of Visual Impairment", "Major Cause of Visual Impairment",
                                  "Hearing Impairment", "Mobility Impairment", "Communication Impairment",
                                  "Cognitive or Intellectual Impairment", "Mental Health Impairment", "Other Impairment",
                                  "Type of Residence", "Source of Referral", "County"])

            client_ids = []
            for client in client_set:
                client_id = client['id']
                if client_id not in client_ids:
                    client_ids.append(client_id)

                    # Translate impairments into the categories asked for
                    client['hearing_impairment'] = 'No'
                    client['mobility_impairment'] = 'No'
                    client['communication_impairment'] = 'No'
                    client['cognition_impairment'] = 'No'
                    client['mental_impairment'] = 'No'
                    client['other_impairment'] = 'No'
                    if client['hearing_loss']:
                        client['hearing_impairment'] = 'Yes'
                    if client['communication']:
                        client['communication_impairment'] = 'Yes'
                    if client['dialysis'] or client['migraine'] or client['geriatric'] or client['allergies'] or client['cancer'] or client['asthma'] or client['pain'] or client['high_bp'] or client['heart'] or client['stroke'] or client['seizure']:
                        client['other_impairment'] = 'Yes'
                    if client['arthritis'] or client['dexterity'] or client['neuropathy'] or client['musculoskeletal']:
                        client['mobility_impairment'] = 'Yes'
                    if client['alzheimers'] or client['memory_loss'] or client['learning_disability']:
                        client['cognition_impairment'] = 'Yes'
                    if client['mental_health'] or client['substance_abuse']:
                        client['mental_impairment'] = 'Yes'

                    # Distill gender options into the three asked for
                    if client["gender"] != 'Male' and client["gender"] != 'Female':
                        client["gender"] = "Did Not Self-Identify Gender"

                    # Sort out race/ethnicity
                    client["hispanic"] = "No"
                    hispanic = False
                    if client["ethnicity"] == "Hispanic or Latino" or client["other_ethnicity"] == "Hispanic or Latino":
                        client["hispanic"] = "Yes"
                        hispanic = True
                    if client["other_ethnicity"] and not hispanic:
                        client["race"] = "2 or More Races"
                    elif client["ethnicity"] == "Other":
                        client["race"] = "Did not self identify Race"
                    else:
                        client["race"] = client["ethnicity"]

                    # Find if case was before this fiscal year
                    if client["note_date"]:
                        # grab the date for the first note
                        year = int(year)
                        quarter = int(quarter)
                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT id, note_date FROM lynx_sipnote where contact_id = '%s' order by id ASC LIMIT 1;""" % (client_id,))
                            note_set = dictfetchall(cursor)
                        note_year = int(note_set[0]["note_date"].year)
                        note_month = int(note_set[0]["note_date"].month)
                        if note_year > year:
                            client['served'] = "Case open between Oct. 1 - Sept. 30"
                        elif note_year == year:
                            if note_month >= 10:
                                client['served'] = "Case open between Oct. 1 - Sept. 30"
                            else:
                                client['served'] = "Case open prior to Oct. 1"
                        else:
                            client['served'] = "Case open prior to Oct. 1"
                    else:
                        client['served'] = "Unknown"

                    # Mark some referral sources as other
                    if client['referred_by']:
                        if client['referred_by'] == "DOR" or client['referred_by'] == "Alta" or client['referred_by'] == "Physician":
                            client['referred_by'] = 'Other'

                    # Write demographic data to demo csv
                    writer.writerow(
                        [client["name"], client['served'], client['age_group'], client["gender"], client["race"],
                         client["hispanic"], client['degree'], client['eye_condition'], client['hearing_impairment'],
                         client['mobility_impairment'], client['communication_impairment'],
                         client['cognition_impairment'], client['mental_impairment'], client['other_impairment'],
                         client['residence_type'], client['referred_by'], client['county']])

            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


def units_to_hours(units):
    minutes = units * 15
    hours = minutes / 60
    return hours


def hours_to_units(hours):
    minutes = hours * 60
    units = minutes / 15
    return units


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# This will not work past 2099 ;)
def get_fiscal_year(year):
    year_str = str(year)
    last_digits = year_str[-2:]
    last_digits_int = int(last_digits)
    year_inc = last_digits_int + 1
    year_inc = str(year_inc)
    if len(year_inc) == 1:
        fiscal_year = year_str + '-0' + year_inc
    else:
        fiscal_year = year_str + '-' + year_inc
    return fiscal_year


def get_quarter(month):
    if month:
        month = int(month)
        if month == 10 or month == 11 or month == 12:
            q = 1
        elif month == 1 or month == 2 or month == 3:
            q = 2
        elif month == 4 or month == 5 or month == 6:
            q = 3
        elif month == 7 or month == 8 or month == 9:
            q = 4
        else:
            return 0
        return q
    else:
        return 0


def boolean_transform(var):
    if var == 1 or var == '1' or var:
        value = "Yes"
    else:
        value = "No"

    return value


def plan_evaluation(progress, previous=None):
    if progress == "Plan complete, feeling more confident in ability to maintain living situation":
        status = "Increased"
        rank = 3
    elif progress == "Plan complete, no difference in ability to maintain living situation":
        status = "Maintained"
        rank = 2
    elif progress == "Plan complete, feeling less confident in ability to maintain living situation":
        status = "Decreased"
        rank = 1
    else:
        status = "Not Assessed"
        rank = 0

    if previous == "Increased":
        p_rank = 3
    elif previous == "Maintained":
        p_rank = 2
    elif previous == "Decreased":
        p_rank = 1
    else:
        p_rank = 0

    if rank < p_rank:
        status = previous

    return status


def assess_evaluation(progress, previous=None):
    status = progress
    if progress == "Assessed, improved independence" or progress == 'Assessed with improved independence':
        rank = 3
    elif progress == "Assessed, maintained independence" or progress == 'Assessed and maintained independence':
        rank = 2
    elif progress == "Assessed, decreased independence" or progress == 'Assessed with decreased independence':
        rank = 1
    else:
        rank = 0

    if previous == "Assessed, improved independence" or previous == 'Assessed with improved independence':
        p_rank = 3
    elif previous == "Assessed, maintained independence" or previous == 'Assessed and maintained independence':
        p_rank = 2
    elif previous == "Assessed, decreased independence" or previous == 'Assessed with decreased independence':
        p_rank = 1
    else:
        p_rank = 0

    if rank < p_rank:
        status = previous

    return status


def replace_characters(a_string, remove_characters):
    if a_string:
        for character in remove_characters:
            a_string = a_string.replace(character, "")

    return a_string


@login_required
def contact_list(request):
    if request.method == 'GET':
        excel = request.GET.get('excel', False)
        strict = True
        f = ContactFilter(request.GET, queryset=ContactInfoView.objects.all().order_by(Lower('full_name')))

        client_condensed = {}
        for client in f.qs:
            if client.id in client_condensed:
                if client_condensed[client.id]['full_phone'] != client.full_phone and client.full_phone is not None:
                    client_condensed[client.id]['full_phone'] = client_condensed[client.id]['full_phone'] + ', ' + client.full_phone
                if client_condensed[client.id]['email'] != client.email and client.email is not None:
                    client_condensed[client.id]['email'] = client_condensed[client.id]['email'] + ', ' + client.email
                if client_condensed[client.id]['zip_code'] != client.zip_code and client.zip_code is not None:
                    client_condensed[client.id]['zip_code'] = client_condensed[client.id]['zip_code'] + ', ' + client.zip_code
                if client_condensed[client.id]['county'] != client.county and client.county is not None:
                    client_condensed[client.id]['county'] = client_condensed[client.id]['county'] + ', ' + client.county
                if client_condensed[client.id]['bad_address'] != client.bad_address and client.bad_address is not None:
                    client_condensed[client.id]['bad_address'] = client_condensed[client.id]['bad_address'] + ', ' + client.bad_address
                if client_condensed[client.id]['do_not_contact'] != client.do_not_contact and client.do_not_contact is not None:
                    client_condensed[client.id]['do_not_contact'] = client_condensed[client.id]['do_not_contact'] + ', ' + client.do_not_contact
                if client_condensed[client.id]['remove_mailing'] != client.remove_mailing and client.remove_mailing is not None:
                    client_condensed[client.id]['remove_mailing'] = client_condensed[client.id]['remove_mailing'] + ', ' + client.remove_mailing
            else:
                client_condensed[client.id] = {}
                client_condensed[client.id]['full_phone'] = client.full_phone if client.full_phone is not None else ''
                client_condensed[client.id]['full_name'] = client.full_name if client.full_name is not None else ''
                client_condensed[client.id]['first_name'] = client.first_name if client.first_name is not None else ''
                client_condensed[client.id]['last_name'] = client.last_name if client.last_name is not None else ''
                client_condensed[client.id]['email'] = client.email if client.email is not None else ''
                client_condensed[client.id]['intake_date'] = client.intake_date if client.intake_date is not None else ''
                client_condensed[client.id]['zip_code'] = client.zip_code if client.zip_code is not None else ''
                client_condensed[client.id]['county'] = client.county if client.county is not None else ''
                client_condensed[client.id]['age_group'] = client.age_group if client.age_group is not None else ''
                client_condensed[client.id]['address_one'] = client.address_one if client.address_one is not None else ''
                client_condensed[client.id]['address_two'] = client.address_two if client.address_two is not None else ''
                client_condensed[client.id]['suite'] = client.suite if client.suite is not None else ''
                client_condensed[client.id]['city'] = client.city if client.city is not None else ''
                client_condensed[client.id]['state'] = client.state if client.state is not None else ''
                client_condensed[client.id]['region'] = client.region if client.region is not None else ''
                client_condensed[client.id]['bad_address'] = client.bad_address if client.bad_address is not None else ''
                client_condensed[client.id]['do_not_contact'] = client.do_not_contact if client.do_not_contact is not None else ''
                client_condensed[client.id]['deceased'] = client.deceased if client.deceased is not None else ''
                client_condensed[client.id]['remove_mailing'] = client.remove_mailing if client.remove_mailing is not None else ''
                client_condensed[client.id]['active'] = client.active if client.active is not None else ''
                client_condensed[client.id]['sip_client'] = client.sip_client if client.sip_client is not None else ''
                client_condensed[client.id]['core_client'] = client.core_client if client.core_client is not None else ''

        if excel == 'true':
            filename = "Lynx Search Results"
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ["Full Name", "First Name", "Last Name", "Intake Date", "Age Group", "County", "Email", "Phone",
                 "Address 1", "Address 2", "Suite", "City", "State", "Zip Code", "Region", "Bad Address",
                 "Do Not Contact", "Deceased", "Remove Mailing", "Active", "SIP Client", 'Core Client'])
            for key, client in client_condensed.items():
                client['bad_address'] = "Bad Address" if client['bad_address'] is not None else ''
                client['do_not_contact'] = "Do Not Contact" if client['do_not_contact'] is not None else ''
                client['deceased'] = "Deceased" if client['deceased'] is not None else ''
                client['active'] = "Active" if client['active'] is not None else ''
                client['sip_client'] = "SIP Client" if client['sip_client'] is not None else ''
                client['core_client'] = "Core Client" if client['core_client'] is not None else ''
                client['remove_mailing'] = "Remove from Mailing List" if client['remove_mailing'] is not None else ''

                writer.writerow(
                    [client['full_name'], client['first_name'], client['last_name'], client['intake_date'],
                     client['age_group'], client['county'], client['email'], client['full_phone'],
                     client['address_one'], client['address_two'], client['suite'], client['city'], client['state'],
                     client['zip_code'], client['region'], client['bad_address'], client['do_not_contact'],
                     client['deceased'], client['remove_mailing'], client['active'], client['sip_client'],
                     client['core_client']])
            return response

    else:
        f = ContactFilter()
        client_condensed = {}
    return render(request, 'lynx/contact_search.html', {'filter': f, 'client_list': client_condensed})


@login_required
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


class ManualView(LoginRequiredMixin, TemplateView):
    template_name = 'lynx/manual.html'


@login_required
def email_update(request):
    username = settings.EMAIL_HOST_USER

    send_mail("Address Changes",
                "Did it work?",
                username,
                ['mjtolentino247@gmail.com'],
                fail_silently=False,
                )

    return HttpResponse('Mail successfully sent')


@login_required
def get_volunteers(request):
    if request.method == 'GET':
        test = 1
    else:
        volunteer_condensed = {}
    return render(request, 'lynx/contact_search.html', {'filter': f, 'volunteer_list': volunteer_condensed})

    query = request.GET.get('q')
    if query:
        object_list = Contact.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name')
        ).annotate(
            zip_code=F('address__zip_code')
        ).annotate(
            county=F('address__county')
        ).annotate(
            intake_date=F('intake__intake_date')
        ).annotate(
            email_address=F('email__email')
        ).filter(
            Q(volunteer_check=1) & (
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(zip_code__icontains=query) |
                Q(county__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(intake_date__icontains=query) |
                Q(email_address__icontains=query)
            )
        )

        object_list = object_list.order_by(Lower('last_name'), Lower('first_name'), 'id')
        paginator = Paginator(object_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    return render(request, 'lynx/client_advanced_search.html', {'page_obj': page_obj})