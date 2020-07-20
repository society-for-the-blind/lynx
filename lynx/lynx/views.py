from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.views.generic import DetailView, ListView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import connection

import csv
from datetime import datetime
from openpyxl import Workbook
import logging

from .models import Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Volunteer
from .forms import ContactForm, IntakeForm, IntakeNoteForm, EmergencyForm, AddressForm, EmailForm, PhoneForm, \
    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm, BillingReportForm, SipDemographicReportForm, \
    VolunteerForm, SipCSFReportForm


logger = logging.getLogger(__name__)


@login_required
def index(request):
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return render(request, 'lynx/index.html', context)


@login_required
def client_list_view(request):
    clients = Contact.objects.filter(active=1).order_by('last_name', 'first_name')
    return render(request, 'lynx/contact_list.html', {'clients': clients})


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
            form = form.save()
            contact_id = form.pk
            address_form = address_form.save(commit=False)
            phone_form = phone_form.save(commit=False)
            email_form = email_form.save(commit=False)
            if hasattr(address_form, 'address_one'):
                address_form.contact_id = contact_id
                address_form.save()
            if hasattr(phone_form, 'phone'):
                phone_form.contact_id = contact_id
                phone_form.save()
            if hasattr(email_form, 'email'):
                email_form.contact_id = contact_id
                email_form.save()
            return HttpResponseRedirect(reverse('lynx:add_intake',  args=(contact_id,)))
    return render(request, 'lynx/add_contact.html', {'address_form': address_form, 'phone_form': phone_form,
                                                     'email_form': email_form, 'form': form})


@login_required
def add_intake(request, contact_id):
    form = IntakeForm()
    if request.method == 'POST':
        form = IntakeForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_intake.html', {'form': form})


# @login_required
# def add_contact_information(request, contact_id):
#     address_form = AddressForm()
#     phone_form = PhoneForm()
#     email_form = EmailForm()
#     emergency_form = EmergencyForm()
#     if request.method == 'POST':
#         address_form = AddressForm(request.POST)
#         phone_form = PhoneForm(request.POST)
#         email_form = EmailForm(request.POST)
#         emergency_form = EmergencyForm(request.POST)
#         if address_form.is_valid() & phone_form.is_valid() & email_form.is_valid() & emergency_form.is_valid():
#             if address_form.address_one:
#                 address_form = address_form.save(commit=False)
#                 address_form.contact_id = contact_id
#                 address_form.save()
#             if phone_form.phone:
#                 phone_form = phone_form.save(commit=False)
#                 phone_form.contact_id = contact_id
#                 phone_form.save()
#             if email_form.email:
#                 email_form = email_form.save(commit=False)
#                 email_form.contact_id = contact_id
#                 email_form.save()
#             if emergency_form.name:
#                 emergency_form = emergency_form.save(commit=False)
#                 emergency_form.contact_id = contact_id
#                 emergency_form.save()
#             return HttpResponseRedirect(reverse('lynx:add_intake',  args=(contact_id,)))
#     return render(request, 'lynx/add_contact_information.html', {'address_form': address_form, 'phone_form': phone_form,
#                                                     'email_form': email_form, 'emergency_form': emergency_form})


@login_required
def add_sip_note(request, contact_id):
    form = SipNoteForm()
    if request.method == 'POST':
        form = SipNoteForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_sip_note.html', {'form': form})


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
            form.active = 1
            form.save()
            emergency_contact_id = form.pk
            if phone_form.data['phone']:
                phone_form = phone_form.save(commit=False)
                phone_form.emergency_contact_id = emergency_contact_id
                phone_form.save()
            if email_form.data['email']:
                email_form = email_form.save(commit=False)
                email_form.emergency_contact_id = emergency_contact_id
                email_form.save()

            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_emergency.html', {'phone_form': phone_form, 'email_form': email_form, 'form': form})


@login_required
def add_address(request, contact_id):
    form = AddressForm()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_address.html', {'form': form})


@login_required
def add_email(request, contact_id):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
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
            form.save()
            emergency = EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_email.html', {'form': form})


@login_required
def add_phone(request, contact_id):
    form = PhoneForm()
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_emergency_phone(request, emergency_contact_id):
    form = PhoneForm()
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.emergency_contact_id = emergency_contact_id
            form.active = 1
            form.save()
            emergency = EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_authorization(request, contact_id):
    form = AuthorizationForm()
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_authorization.html', {'form': form})


@login_required
def add_progress_report(request, authorization_id):
    form = ProgressReportForm()
    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail',  args=(authorization_id,)))
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
            form.save()
            if address_form['address_one']:
                address_form = address_form.save(commit=False)
                address_form.contact_id = contact_id
                address_form.save()
            if phone_form.phone:
                phone_form = phone_form.save(commit=False)
                phone_form.contact_id = contact_id
                phone_form.save()
            if email_form.email:
                email_form = email_form.save(commit=False)
                email_form.contact_id = contact_id
                email_form.save()
            return HttpResponseRedirect(reverse('lynx:volunteer_detail',  args=(volunteer_id,)))
    return render(request, 'lynx/add_volunteer.html', {'address_form': address_form, 'phone_form': phone_form,
                                                     'email_form': email_form, 'form': form, 'contact_form': contact_form})


@login_required
def add_lesson_note(request, authorization_id):
    form = LessonNoteForm()
    authorization = Authorization.objects.get(id=authorization_id)
    client = Contact.objects.get(id=authorization.contact_id)
    if authorization.authorization_type == 'Hours':
        auth_type = 'individual'
    else:
        auth_type = 'group'
    if request.method == 'POST':
        form = LessonNoteForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail',  args=(authorization_id,)))
    return render(request, 'lynx/add_lesson_note.html', {'form': form, 'client': client, 'auth_type': auth_type})

#
# class ContactListView(LoginRequiredMixin, ListView):
#
#     model = Contact
#     paginate_by = 100  # if contact_id
#     # pagination is desired
#
#     ordering = ['last_name', 'first_name']


@login_required
def client_result_view(request):
    query = request.GET.get('q')
    if query:
        object_list = Contact.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        object_list = None
    return render(request, 'lynx/client_search.html', {'object_list': object_list})


class ContactResultsView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'client_search.html'

    def get_queryset(self): # new
        query = self.request.GET.get('q')
        if query:
            object_list = Contact.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        else:
            object_list = None
        return object_list


class ContactDetailView(LoginRequiredMixin, DetailView):

    model = Contact

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        context['address_list'] = Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = Phone.objects.filter(contact_id=self.kwargs['pk'])
        context['email_list'] = Email.objects.filter(contact_id=self.kwargs['pk'])
        context['intake_list'] = Intake.objects.filter(contact_id=self.kwargs['pk'])
        context['authorization_list'] = Authorization.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['note_list'] = IntakeNote.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['sip_list'] = SipNote.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['emergency_list'] = EmergencyContact.objects.filter(contact_id=self.kwargs['pk'])
        context['form'] = IntakeNoteForm
        return context

    def post(self, request, *args, **kwargs):
        form = IntakeNoteForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = self.kwargs['pk']
            form.user_id = request.user.id
            form.save()
            # form.user.add(*[request.user])
            action = "/lynx/client/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)


class AuthorizationDetailView(LoginRequiredMixin, DetailView):

    model = Authorization

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AuthorizationDetailView, self).get_context_data(**kwargs)
        context['report_list'] = ProgressReport.objects.filter(authorization_id=self.kwargs['pk'])
        context['note_list'] = LessonNote.objects.filter(authorization_id=self.kwargs['pk']).order_by('-created')
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
            note['hours'] = float(note['billed_units'])/4
        total_hours = units_to_hours(total_units)
        if authorization[0]['billing_rate'] is None:
            context['total_billed'] = 'Need to enter billing rate'
            context['rate'] = 'Need to enter billing rate'
        else:
            if authorization[0]['authorization_type'] == 'Classes':
                context['rate'] = '$' + str(authorization[0]['billing_rate']) + '/class'
                context['total_billed'] = '$' + str(class_count * float(authorization[0]['billing_rate']))
                context['total_hours'] = class_count
            if authorization[0]['authorization_type'] == 'Hours':
                context['rate'] = '$' + str(authorization[0]['billing_rate']) + '/hour'
                context['total_billed'] = '$' + str(total_hours * float(authorization[0]['billing_rate']))
                context['total_hours'] = total_hours
        if authorization[0]['total_time'] is None:
            context['remaining_hours'] = "Need to enter total time"
        else:
            if authorization[0]['authorization_type'] == 'Classes':
                remaining_hours = float(authorization[0]['total_time']) - class_count
                # remaining_hours = units_to_hours(remaining)
                context['remaining_hours'] = remaining_hours
            if authorization[0]['authorization_type'] == 'Hours':
                remaining_hours = float(authorization[0]['total_time']) - total_hours
                # remaining_hours = units_to_hours(remaining)
                context['remaining_hours'] = remaining_hours


        context['total_notes'] = total_notes
        context['total_time'] = authorization[0]['total_time']

        context['total_present'] = total_present
        # context['total_instruction'] = total_instruction
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

        # print(context)
        report = ProgressReport.objects.filter(id=self.kwargs['pk']).values()
        auth_id = report[0]['authorization_id']
        month_number = report[0]['month']
        if len(month_number) >2:
        # if report[0]['month']:
            month = report[0]['month']
            month_number = MONTHS[month]
        # else:
        #     created = report[0]['created']
        #     date_created = datetime.strptime(created, "%Y-%m-%d %I:%M:%S")
        #     month_number = date_created.month
        notes = LessonNote.objects.filter(authorization_id=auth_id).filter(date__month=month_number).values() #TODO: filter by year, wait until live data in
        all_notes = LessonNote.objects.filter(authorization_id=auth_id).values()
        authorization = Authorization.objects.filter(id=auth_id).values()

        total_units = 0
        all_units = 0
        class_count = 0
        month_count = 0

        for note in all_notes:
            if note['billed_units']:
                units = float(note['billed_units'])
                all_units += units
                class_count += 1
        for note in notes:
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units
                month_count += 1
        if authorization[0]['authorization_type'] == 'Classes':
            context['total_hours'] = class_count #used in total
            context['month_used'] = month_count #used this month
            context['total_time'] = authorization[0]['total_time']
        if authorization[0]['authorization_type'] == 'Hours':
            total_hours = units_to_hours(all_units)
            context['total_hours'] = total_hours #used in total
            month_used = units_to_hours(total_units)
            context['month_used'] = month_used #used this month
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

        auth_id = self.kwargs['pk']
        report = ProgressReport.objects.filter(authorization_id=auth_id).values() #TODO: filter by month and year, wait until live data in
        notes = LessonNote.objects.filter(authorization_id=auth_id).filter(date__month=month).values() #TODO: filter by year, wait until live data in
        authorization = Authorization.objects.filter(id=auth_id).values()

        total_units = 0
        total_notes = 0
        # context['instructors'] = report[0]['instructor']
        for note in notes:
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units
                total_notes += 1

        if authorization[0]['authorization_type'] == 'Classes':
            context['month_used'] = total_notes #used this month
        if authorization[0]['authorization_type'] == 'Hours':
            month_used = units_to_hours(total_units)
            context['month_used'] = month_used #used this month
        context['total_time'] = authorization[0]['total_time']

        return context


class VolunteerDetailView(LoginRequiredMixin, DetailView):

    model = Volunteer

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VolunteerDetailView, self).get_context_data(**kwargs)
        context['contact_list'] = Contact.objects.filter(id=self.kwargs['pk'])
        context['address_list'] = Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = Phone.objects.filter(contact_id=self.kwargs['pk'])
        context['email_list'] = Email.objects.filter(contact_id=self.kwargs['pk'])
        context['emergency_list'] = EmergencyContact.objects.filter(contact_id=self.kwargs['pk'])
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
              'hire_date', 'payment_source', 'referred_by']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["other_languages"].label = "Other Language(s)"
        form.fields["other_ethnicity"].label = "Ethnicity (if other)"
        form.fields["crime"].label = "Have you been convicted of a crime?"
        form.fields["crime_info"].label = "If yes, what and when did the convictions occur? What county did this conviction occur in?"
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
    fields = ['name', 'emergency_address_one', 'emergency_address_two', 'emergency_city', 'emergency_state', 'emergency_zip_code',
              'emergency_country', 'phone_day', 'phone_other', 'emergency_notes', 'emergency_email']
    template_name_suffix = '_edit'


class LessonNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = LessonNote
    fields = ['date', 'attendance', 'instructional_units', 'billed_units', 'students_no', 'successes',
              'obstacles', 'recommendations', 'note']
    template_name_suffix = '_edit'


class ProgressReportUpdateView(LoginRequiredMixin, UpdateView):
    model = ProgressReport
    fields = ['month', 'instructor', 'accomplishments', 'short_term_goals', 'short_term_goals_time',
              'long_term_goals', 'long_term_goals_time', 'client_behavior']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["client_behavior"].label = "Client Attendance and Behavior"
        form.fields["short_term_goals"].label = "Short Term Learning Goals"
        form.fields["short_term_goals_time"].label = "Estimated Time for Short Term Goals"
        form.fields["long_term_goals"].label = "Long Term Learning Goals"
        form.fields["long_term_goals_time"].label = "Estimated Time for Long Term Goals"
        return form


class SipNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = SipNote
    fields = ['note', 'note_date', 'vision_screening', 'treatment', 'at_devices', 'at_services', 'independent_living',
              'orientation', 'communications', 'dls', 'support', 'advocacy', 'counseling', 'information', 'services',
              'retreat', 'in_home', 'seminar', 'modesto', 'group', 'community']
    template_name_suffix = '_edit'


class AuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Authorization
    fields = ['intake_service_area', 'authorization_number', 'authorization_type', 'start_date', 'end_date',
              'total_time', 'billing_rate', 'outside_agency', 'student_plan', 'notes']
    template_name_suffix = '_edit'


def billing_report(request):
    form = BillingReportForm()
    if request.method == 'POST':
        form = BillingReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area, auth.authorization_type, auth.authorization_number,
                                    ln.billed_units, auth.billing_rate, oa.agency as outside_agency
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
                authorization_number = report['authorization_number']
                billing_rate = float(report['billing_rate'])
                if authorization_number in reports.keys():
                    if report['authorization_type'] == 'Hours':
                        if report['billed_units'] and reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = (float(report['billed_units'])/4) + float(reports[authorization_number]['billed_time'])
                            loop_amount = billing_rate * (float(report['billed_units'])/4)
                            reports[authorization_number]['amount'] = (billing_rate * float(reports[authorization_number]['billed_time']))
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = float(report['billed_units'])/4
                            loop_amount = billing_rate * (float(report['billed_units'])/4)
                            reports[authorization_number]['amount'] = billing_rate * float(reports[authorization_number]['billed_time'])
                    if report['authorization_type'] == 'Classes':
                        if report['billed_units'] and reports[authorization_number]['billed_time']:
                            reports[authorization_number]['billed_time'] = 1 + float(reports[authorization_number]['billed_time'])
                            reports[authorization_number]['amount'] = billing_rate + reports[authorization_number]['amount']
                            loop_amount = billing_rate
                        elif report['billed_units']:
                            reports[authorization_number]['billed_time'] = 1
                            reports[authorization_number]['amount'] = loop_amount = billing_rate
                    total_amount += loop_amount
                else:
                    service_area = report['service_area']
                    authorization_type = report['authorization_type']
                    outside_agency = report['outside_agency']
                    client = report['name']
                    billed_units = report['billed_units']
                    if authorization_type == 'Hours':
                        rate = str(billing_rate) + '/hour'
                    else:
                        rate = str(billing_rate) + '/class'

                    if report['authorization_type'] == 'Hours':
                        billed_time = float(report['billed_units'])/4
                        amount = billing_rate * float(billed_time)
                    elif report['authorization_type'] == 'Classes':
                        if billed_units:
                            amount = billing_rate
                            billed_time = 1
                        else:
                            amount = 0
                    else:
                        amount = 0

                    total_amount += amount
                    auth = {'service_area': service_area, 'authorization_number': authorization_number,
                            'authorization_type': authorization_type, 'outside_agency': outside_agency, 'rate': rate,
                            'client': client, 'billed_time': billed_time, 'amount': amount}
                    reports[authorization_number] = auth

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client', 'Service Area', 'Authorization', 'Authorization Type', 'Billed Time (Classes/Hours)', 'Billing Rate',
                 'Amount', 'Payment Source'])

            for key, value in reports.items():
                in_hours = 'No hours'
                if value['billed_time']:
                    in_hours = float(value['billed_time'])
                    total_hours += int(value['billed_time'])

                writer.writerow([value['client'], value['service_area'], value['authorization_number'],
                                 value['authorization_type'], in_hours, value['rate'], value['amount'],
                                 value['outside_agency']])

            writer.writerow(['', '', '', '', total_hours, '', '$' + str(total_amount), ''])

            return response

    return render(request, 'lynx/billing_report.html', {'form': form})


def sip_demographic_report(request):
    form = SipDemographicReportForm()
    if request.method == 'POST':
        form = SipDemographicReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            fiscal_months = ['10', '11', '12', '1', '2', '3', '4', '5', '6', '7', '8', '9']

            first = True
            month_string = ''
            for month_no in fiscal_months:
                if month_no == month:
                    break
                else:
                    if first:
                        month_string = """SELECT client.id FROM lynx_sipnote AS sip 
                        LEFT JOIN lynx_contact AS client ON client.id = sip.contact_id 
                        WHERE extract(month FROM sip.note_date) = """ + month_no
                        first = False
                    else:
                        month_string = month_string + ' or extract(month FROM sip.note_date) = ' + month_no

            if len(month_string) > 0:
                month_string = " and c.id not in (" + month_string + ')'

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, c.id as id, int.created as date, int.age_group, int.gender, int.ethnicity,
                    int.degree, int.eye_condition, int.eye_condition_date, int.education, int.living_arrangement, int.residence_type,
                    int.dialysis, int.stroke, int.seizure, int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma,
                    int.cancer, int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, int.memory_loss,
                    int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.referred_by
                    FROM lynx_sipnote ls
                    left JOIN lynx_contact as c  on c.id = ls.contact_id
                    left JOIN lynx_intake as int  on int.contact_id = c.id
                    where extract(month FROM ls.note_date) = '%s' and extract(year FROM ls.note_date) = '%s' and c.sip_client is true %s
                    order by c.last_name, c.first_name;""" % (month, year, month_string))
                client_set = dictfetchall(cursor)
                #TODO make sure this works with year

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'

            writer = csv.writer(response)
            writer.writerow(
                ['Client Name', 'Age', 'Gender', 'Race/Ethnicity', 'Visual Impairment at Time of Intake', 'Major Cause of Visual Impairment',
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
                    [client['name'], client['age_group'], client['gender'], client['ethnicity'], client['degree'],
                     client['eye_condition'], impairments, client['eye_condition_date'], client['education'],
                     client['living_arrangement'], client['residence_type'], client['referred_by']])

            return response

    return render(request, 'lynx/billing_report.html', {'form': form})


def sip_csf_report(request):
    form = SipCSFReportForm()
    if request.method == 'POST':
        form = SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            wb1 = Workbook()
            for i in range(n):
                ws = wb1.create_sheet("run " + str(i))

                # code on formatting sheet, optimization problem

            fiscal_months = ['10', '11', '12', '1', '2', '3', '4', '5', '6', '7', '8', '9']

            COUNTIES = (("Alameda", "Alameda"), ("Alpine", "Alpine"), ("Amador", "Amador"), ("Butte", "Butte"),
                        ("Colusa", "Colusa"), ("Calaveras", "Calaveras"), ("Contra Costa", "Contra Costa"),
                        ("Del Norte", "Del Norte"), ("El Dorado", "El Dorado"), ("Fresno", "Fresno"),
                        ("Glenn", "Glenn"), ("Humboldt", "Humboldt"), ("Imperial", "Imperial"), ("Inyo", "Inyo"),
                        ("Kern", "Kern"), ("Kings", "Kings"), ("Klamath", "Klamath"), ("Lake", "Lake"),
                        ("Lassen", "Lassen"), ("Los Angeles", "Los Angeles"), ("Madera", "Madera"), ("Marin", "Marin"),
                        ("Mariposa", "Mariposa"), ("Mendocino", "Mendocino"), ("Merced", "Merced"), ("Modoc", "Modoc"),
                        ("Mono", "Mono"), ("Monterey", "Monterey"), ("Napa", "Napa"), ("Nevada", "Nevada"),
                        ("Orange", "Orange"), ("Placer", "Placer"), ("Plumas", "Plumas"), ("Riverside", "Riverside"),
                        ("Sacramento", "Sacramento"), ("San Benito", "San Benito"), ("San Bernardino", "San Bernardino"),
                        ("San Diego", "San Diego"), ("San Francisco", "San Francisco"), ("San Joaquin", "San Joaquin"),
                        ("San Luis Obispo", "San Luis Obispo"), ("San Mateo", "San Mateo"),
                        ("Santa Barbara", "Santa Barbara"), ("Santa Clara", "Santa Clara"), ("Santa Cruz", "Santa Cruz"),
                        ("Shasta", "Shasta"), ("Sierra", "Sierra"), ("Siskiyou", "Siskiyou"),  ("Solano", "Solano"),
                        ("Sonoma", "Sonoma"), ("Stanislaus", "Stanislaus"), ("Sutter", "Sutter"), ("Tehama", "Tehama"),
                        ("Trinity", "Trinity"), ("Tulare", "Tulare"), ("Tuolumne", "Tuolumne"), ("Ventura", "Ventura"),
                        ("Yolo", "Yolo"), ("Yuba", "Yuba"), ("Other/None", "Other/None"))

            first = True
            month_string = ''
            for month_no in fiscal_months:
                if month_no == month:
                    break
                else:
                    if first:
                        month_string = """SELECT client.id FROM lynx_sipnote AS sip 
                        LEFT JOIN lynx_contact AS client ON client.id = sip.contact_id 
                        WHERE extract(month FROM sip.note_date) = """ + month_no
                        first = False
                    else:
                        month_string = month_string + ' or extract(month FROM sip.note_date) = ' + month_no

            if len(month_string) > 0:
                month_string = " and c.id not in (" + month_string + ')'

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, c.id as id, int.created as date, int.age_group, int.gender, int.ethnicity,
                    int.degree, int.eye_condition, int.eye_condition_date, int.education, int.living_arrangement, int.residence_type,
                    int.dialysis, int.stroke, int.seizure, int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma,
                    int.cancer, int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, int.memory_loss,
                    int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.referred_by
                    FROM lynx_sipnote ls
                    left JOIN lynx_contact as c  on c.id = ls.contact_id
                    left JOIN lynx_intake as int  on int.contact_id = c.id
                    where extract(month FROM ls.note_date) = '%s' and extract(year FROM ls.note_date) = '%s' and c.sip_client is true %s
                    order by c.last_name, c.first_name;""" % (month, year, month_string))
                client_set = dictfetchall(cursor)
                #TODO make sure this works with year

            filename = "Core Lynx Excel Billing - " + month + " - " + year
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'



            wb1.save('outfile.xlsx')
            return response

    return render(request, 'lynx/billing_report.html', {'form': form})


def units_to_hours(units):
    minutes = units * 15
    hours = minutes/60
    return hours


def hours_to_units(hours):
    minutes = hours * 60
    units = minutes/15
    return units


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
