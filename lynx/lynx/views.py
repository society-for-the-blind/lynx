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

from .models import Contact, Address, Phone, Email, Intake, Referral, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote
from .forms import ContactForm, IntakeForm, IntakeNoteForm, EmergencyForm, AddressForm, EmailForm, PhoneForm, \
    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm


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
            address_form.contact_id = contact_id
            address_form.save()
            phone_form = phone_form.save(commit=False)
            phone_form.contact_id = contact_id
            phone_form.save()
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
            address_form = address_form.save(commit=False)
            address_form.contact_id = contact_id
            address_form.save()
            phone_form = phone_form.save(commit=False)
            phone_form.contact_id = contact_id
            phone_form.save()
            email_form = email_form.save(commit=False)
            email_form.contact_id = contact_id
            email_form.save()
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
    if request.method == 'POST':
        form = EmergencyForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client',  args=(contact_id,)))
    return render(request, 'lynx/add_emergency.html', {'form': form})


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
        context['authorization_list'] = Authorization.objects.filter(contact_id=self.kwargs['pk'])
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
                # if authorization['authorization_type'] == 'Classes':
                #     units = float(note['billed_units']/8)
                # if authorization['authorization_type'] == 'Hours':
                units = float(note['billed_units'])
                total_units += units
            if note['instructional_units']:
                i_units = float(note['instructional_units'])
                total_instruction += i_units

        context['total_billed'] = total_units * float(authorization[0]['billing_rate'])
        remaining = float(authorization[0]['total_time']) - total_units
        remaining_hours = units_to_hours(remaining)
        total_hours = units_to_hours(total_units)
        context['total_hours'] = total_hours
        context['total_notes'] = total_notes
        context['remaining_hours'] = remaining_hours
        context['total_present'] = total_present
        context['total_instruction'] = total_instruction
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
        return context


class LessonNoteDetailView(LoginRequiredMixin, DetailView):

    model = LessonNote


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'middle_name', 'last_name', 'company', 'do_not_contact', 'donor', 'deceased',
              'remove_mailing', 'active', 'contact_notes', 'sip_client', 'core_client', 'careers_plus', 'careers_plus_youth', 'volunteer', 'access_news', 'other_services']
    template_name_suffix = '_edit'


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['address_one', 'address_two', 'suite', 'city', 'state', 'zip_code', 'county', 'country', 'region',
              'cross_streets', 'bad_address', 'billing', 'address_notes']
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
    fields = ['intake_date', 'gender', 'pronouns', 'birth_date', 'ethnicity', 'other_ethnicity', 'income',
              'first_language', 'second_language', 'other_languages', 'education', 'living_arrangement',
              'residence_type', 'performs_tasks', 'notes', 'confidentiality', 'dmv', 'work_history',
              'veteran', 'active', 'crime', 'crime_info', 'crime_other', 'parole', 'parole_info',
              'crime_history', 'previous_training', 'training_goals', 'training_preferences', 'other', 'eye_condition',
              'eye_condition_date', 'degree', 'prognosis', 'diabetes', 'dialysis', 'hearing_loss', 'mobility', 'stroke',
              'seizure', 'heart', 'high_bp', 'neuropathy', 'pain', 'asthma', 'cancer', 'allergies', 'mental_health',
              'substance_abuse', 'memory_loss', 'learning_disability', 'other_medical', 'medications', 'medical_notes',
              'hired', 'arthritis', 'musculoskeletal', 'alzheimers', 'hobbies', 'employment_goals']
    template_name_suffix = '_edit'


class IntakeNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = IntakeNote
    fields = ['note']
    template_name_suffix = '_edit'


class EmergencyContactUpdateView(LoginRequiredMixin, UpdateView):
    model = EmergencyContact
    fields = ['name', 'emergency_address_one', 'emergency_address_two', 'emergency_city', 'emergency_state', 'emergency_zip_code',
              'emergency_country', 'phone_day', 'phone_other', 'emergency_notes']
    template_name_suffix = '_edit'


def units_to_hours(units):
    minutes = units * 15
    hours = minutes/60
    return hours


def hours_to_units(hours):
    minutes = hours * 60
    units = minutes/15
    return units
