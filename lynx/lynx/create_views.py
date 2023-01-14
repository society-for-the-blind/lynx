import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from .forms import (ContactForm, IntakeForm, EmergencyForm, AddressForm, EmailForm, PhoneForm,
                    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm,
                    VolunteerForm, SipPlanForm, SipNoteBulkForm, VolunteerHoursForm, VaccineForm, AssignmentForm)
from .models import (Contact, EmergencyContact, Authorization, LessonNote, SipPlan)
from .support_functions import get_fiscal_year, get_quarter

logger = logging.getLogger(__name__)


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
            form.instructor = request.user.first_name + request.user.last_name
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
            form.instructor = request.user.first_name + request.user.last_name
            form.plan_name = request.POST.get('plan_date') + ' - ' + request.POST.get(
                'plan_type') + ' - ' + form.instructor
            # form.plan_date = request.POST.get('start_date')
            form.contact_id = contact_id
            form.user_id = request.user.id

            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_sip_plan.html', {'form': form})


@login_required
def add_sip_note_bulk(request):
    form = SipNoteBulkForm()
    client_list = Contact.objects.filter(sip_client=1).order_by(Lower('last_name'))
    count_range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
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
            form.instructor = request.user.first_name + request.user.last_name
            form.user_id = request.user.id
            form.save()
            for i in count_range:
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
    return render(
        request,
        'lynx/add_sip_note_bulk.html',
        {'form': form, 'client_list': client_list, 'range': count_range}
    )


@login_required
def add_assignments(request, contact_id):
    form = AssignmentForm()
    instructors = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.save()

            username = f'SIP Assignments <{settings.EMAIL_HOST_USER}>'
            message = f"You have a new SIP Assignment by {request.user.first_name} with the following note: {form.note}"
            instructor = User.objects.filter(pk=form.instructor_id).values('email')
            inst_email = instructor[0]['email']
            client_name = form.contact.first_name + " " + form.contact.last_name

            send_mail(client_name,  # subject
                      message,  # message
                      username,  # from email
                      [inst_email],  # recipient list
                      fail_silently=False,
                      )

            return HttpResponseRedirect(reverse('lynx:assignment', args=(contact_id,)))
    return render(request, 'lynx/add_assignments.html',
                  {'form': form, 'instructors': instructors, 'contact_id': contact_id})


def get_sip_plans(request):
    contact_id = request.GET.get('client_id')
    plans = SipPlan.objects.filter(contact_id=contact_id).order_by('-plan_date')
    return render(request, 'lynx/sip_plan_list_options.html', {'plans': plans})


@login_required
def add_emergency(request, contact_id):
    form = EmergencyForm()
    phone_form = PhoneForm()
    if request.method == 'POST':
        phone_form = PhoneForm(request.POST)
        form = EmergencyForm(request.POST)
        if phone_form.is_valid() & form.is_valid():
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

            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_emergency.html',
                  {'phone_form': phone_form, 'form': form})


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
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(contact_id,)))
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
        if (
                address_form.is_valid() and
                phone_form.is_valid() and
                email_form.is_valid() and
                form.is_valid() and
                contact_form.is_valid()
        ):
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
    # note_list = LessonNote.objects.filter(authorization_id=authorization_id)

    client = Contact.objects.get(id=authorization.contact_id)
    if authorization.authorization_type == 'Hours':
        auth_type = 'individual'
    else:
        auth_type = 'group'
    if request.method == 'POST':
        form = LessonNoteForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(authorization_id,)))
    return render(request, 'lynx/add_lesson_note.html', {'form': form, 'client': client, 'auth_type': auth_type,
                                                         'authorization_id': authorization_id})


@login_required
def add_vaccination_record(request, contact_id):
    form = VaccineForm()
    if request.method == 'POST':
        form = VaccineForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_vaccine_record.html', {'form': form})
