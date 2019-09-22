from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.views.generic import DetailView, ListView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

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
def client_list_view(request):
    clients = Contact.objects.all().order_by('last_name', 'first_name')
    return render(request, 'lynx/contact_list.html', {'clients': clients})


class ContactListView(LoginRequiredMixin, ListView):

    model = Contact
    paginate_by = 100  # if contact_id
    # pagination is desired

    ordering = ['last_name', 'first_name']


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


class AuthorizationDetailView(LoginRequiredMixin, DetailView):

    model = Authorization

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AuthorizationDetailView, self).get_context_data(**kwargs)
        context['report_list'] = ProgressReport.objects.filter(authorization_id=self.kwargs['pk'])
        context['note_list'] = LessonNote.objects.filter(authorization_id=self.kwargs['pk']).order_by('-created')
        notes = LessonNote.objects.filter(authorization_id=self.kwargs['pk']).values()
        auth = Authorization.objects.filter(id=self.kwargs['pk']).values()
        total_units = 0
        for note in notes:
            units = float(note['billed_units'])
            total_units += units
        context['total_billed'] = total_units * float(auth[0]['billing_rate'])
        context['remaining_units'] = float(auth[0]['total_time']) - total_units
        context['total_units'] = total_units
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


class ProgressReportDetailView(LoginRequiredMixin, DetailView):

    model = ProgressReport

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgressReportDetailView, self).get_context_data(**kwargs)
        return context


@login_required
def add_lesson_note(request, authorization_id):
    form = LessonNoteForm()
    auth = Authorization.objects.get(id=authorization_id)
    client = Contact.objects.get(id=auth.contact_id)
    if request.method == 'POST':
        form = LessonNoteForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail',  args=(authorization_id,)))
    return render(request, 'lynx/add_lesson_note.html', {'form': form, 'client': client})


class LessonNoteDetailView(LoginRequiredMixin, DetailView):

    model = LessonNote


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'middle_name', 'last_name', 'company', 'do_not_contact', 'donor', 'deceased', 'remove_mailing', 'active', 'contact_notes']
    template_name_suffix = '_edit'


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['address_one', 'address_two', 'suite', 'city', 'state', 'zip_code', 'county', 'country', 'region', 'cross_streets', 'bad_address', 'billing', 'address_notes']
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
    fields = ['intake_date', 'intake_type', 'gender', 'pronouns', 'birth_date', 'ethnicity', 'other_ethnicity', 'income',
              'first_language', 'second_language', 'other_languages', 'education', 'living_arrangement', 'residence_type',
              'preferred_medium', 'performs_tasks', 'notes', 'training', 'orientation', 'confidentiality', 'dmv', 'work_history',
              'veteran', 'member_name', 'active', 'crime', 'crime_info', 'crime_other', 'parole', 'parole_info',
              'crime_history', 'previous_training', 'training_goals', 'training_preferences', 'other', 'eye_condition',
              'eye_condition_date', 'degree', 'prognosis', 'diabetes', 'dialysis', 'hearing_loss', 'mobility', 'stroke',
              'seizure', 'heart', 'high_bp', 'neuropathy', 'pain', 'asthma', 'cancer', 'allergies', 'mental_health',
              'substance_abuse', 'memory_loss', 'learning_disability', 'other_medical', 'medications', 'medical_notes', 'hired']
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
