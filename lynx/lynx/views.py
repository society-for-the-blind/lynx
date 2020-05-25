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

from .models import Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote
from .forms import ContactForm, IntakeForm, IntakeNoteForm, EmergencyForm, AddressForm, EmailForm, PhoneForm, \
    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm, BillingReportForm


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


@login_required
def add_contact_information(request, contact_id):
    address_form = AddressForm()
    phone_form = PhoneForm()
    email_form = EmailForm()
    emergency_form = EmergencyForm()
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        phone_form = PhoneForm(request.POST)
        email_form = EmailForm(request.POST)
        emergency_form = EmergencyForm(request.POST)
        if address_form.is_valid() & phone_form.is_valid() & email_form.is_valid() & emergency_form.is_valid():
            if address_form.address_one:
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
            if emergency_form.name:
                emergency_form = emergency_form.save(commit=False)
                emergency_form.contact_id = contact_id
                emergency_form.save()
            return HttpResponseRedirect(reverse('lynx:add_intake',  args=(contact_id,)))
    return render(request, 'lynx/add_contact_information.html', {'address_form': address_form, 'phone_form': phone_form,
                                                    'email_form': email_form, 'emergency_form': emergency_form})


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
        total_instruction = 0
        for note in notes:
            if note['attendance'] != 'Other':
                total_notes += 1
            if note['attendance'] == 'Present':
                total_present += 1
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units
            # if note['instructional_units']:
            #     i_units = float(note['instructional_units'])
            #     total_instruction += i_units

        if authorization[0]['billing_rate'] is None:
            context['total_billed'] = 'Need to enter billing rate'
            context['rate'] = 'Need to enter billing rate'
        else:
            context['total_billed'] = '$' + str(total_units * float(authorization[0]['billing_rate']))
            if authorization[0]['authorization_type'] == 'Classes':
                context['rate'] = '$' + str(authorization[0]['billing_rate']) + '/class'
            if authorization[0]['authorization_type'] == 'Hours':
                billing = 4 * float(authorization[0]['billing_rate'])
                context['rate'] = '$' + str(billing) + '/hour'
        if authorization[0]['total_time'] is None:
            context['remaining_hours'] = "Need to enter total time"
        else:
            remaining = float(authorization[0]['total_time']) - total_units
            remaining_hours = units_to_hours(remaining)
            context['remaining_hours'] = remaining_hours
        total_hours = units_to_hours(total_units)
        context['total_hours'] = total_hours
        context['total_notes'] = total_notes

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

        # print(context)
        report = ProgressReport.objects.filter(id=self.kwargs['pk']).values()
        notes = LessonNote.objects.filter(authorization_id=report[0]['authorization_id']).values()
        authorization = Authorization.objects.filter(id=report[0]['authorization_id']).values()

        total_units = 0
        for note in notes:
            if note['billed_units']:
                units = float(note['billed_units'])
                total_units += units

            total_hours = units_to_hours(float(authorization[0]['total_time']))
            context['total_hours'] = total_hours
            hours_used = units_to_hours(total_units)
            context['hours_used'] = hours_used
            if authorization[0]['total_time'] is None:
                context['remaining_hours'] = "Need to enter total time"
            else:
                remaining = float(authorization[0]['total_time']) - total_units
                remaining_hours = units_to_hours(remaining)
                context['remaining_hours'] = remaining_hours

        return context


class LessonNoteDetailView(LoginRequiredMixin, DetailView):

    model = LessonNote


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'middle_name', 'last_name', 'company', 'do_not_contact', 'donor', 'deceased',
              'remove_mailing', 'active', 'contact_notes', 'sip_client', 'core_client', 'careers_plus',
              'careers_plus_youth', 'volunteer', 'access_news', 'other_services']
    template_name_suffix = '_edit'


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
                                    order by c.last_name, c.first_name, sa.agency;;""" % (month, year))
                auth_set = dictfetchall(cursor)

            reports = {}
            for report in auth_set:
                # print(report)
                authorization_number = report['authorization_number']
                billing_rate = float(report['billing_rate'])
                if authorization_number in reports.keys():
                    if report['billed_units'] and reports[authorization_number]['billed_time']:
                        reports[authorization_number]['billed_time']  = float(report['billed_units']) + float(reports[authorization_number]['billed_time'])
                        reports[authorization_number]['amount'] = billing_rate * float(reports[authorization_number]['billed_time'])
                    elif report['billed_units']:
                        reports[authorization_number]['billed_time']  = float(report['billed_units'])
                        reports[authorization_number]['amount'] = billing_rate * float(reports[authorization_number]['billed_time'])
                else:
                    service_area = report['service_area']
                    authorization_type = report['authorization_type']
                    outside_agency = report['outside_agency']
                    client = report['name']
                    billed_time = report['billed_units']
                    rate = str(billing_rate * 4) + '/hour'
                    if billed_time:
                        amount = float(billed_time) * billing_rate
                    else:
                        amount = 0
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
                    in_hours = str(float(value['billed_time'])/4)
                writer.writerow([value['client'], value['service_area'], value['authorization_number'],
                                 value['authorization_type'], in_hours, value['rate'], value['amount'],
                                 value['outside_agency']])

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
