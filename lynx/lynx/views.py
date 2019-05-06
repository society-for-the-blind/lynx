from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.views.generic import DetailView, ListView, FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Contact, Address, Phone, Email, Intake, Referral, IntakeNote, EmergencyContact
from .forms import IntakeFormContact, IntakeFormOther, IntakeFormCriminal, IntakeFormEmergency, IntakeFormHistory, \
    IntakeFormAddress, IntakeFormEmail, IntakeFormPhone, IntakeNoteForm


@login_required
def index(request):
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return render(request, 'lynx/index.html', context)


@login_required
def client_list(request):
    template = loader.get_template('lynx/clients.html')
    context = {
        "message": "Welcome to Lynx, the Client Management Tool for Society for the Blind"
    }
    return HttpResponse(template.render(context, request))


# @login_required
# def add_intake1(request):
#     if request.method == 'POST':
#         intake_form = IntakeFormContact(request.POST)
#         if intake_form.is_valid():
#             intake_form.save()
#             return HttpResponseRedirect("/lynx/add-intake/2/")
#         else:
#             print(intake_form.errors)
#
#     else:
#         intake_form = IntakeFormContact()
#
#     return render(request, 'lynx/new_intake_1.html', {'intake_form': intake_form})


class IntakeFormView(LoginRequiredMixin, FormView):

    model = Intake
    template_name = 'lynx/new_intake_1.html'
    form_class = IntakeFormContact
    success_url = 'lynx/add-intake/2/'

# def add_intake1(request):
#     action = "/lynx/add-intake/2/"
#
#     if request.method == 'POST':
#         intake_form = IntakeFormContact(request.POST)
#         intake_form_other = IntakeFormOther(request.POST)
#         intake_form_emergency = IntakeFormEmergency(request.POST)
#         intake_form_address = IntakeFormAddress(request.POST)
#         intake_form_email = IntakeFormEmail(request.POST)
#         intake_form_phone = IntakeFormPhone(request.POST)
#         if all([intake_form.is_valid(), intake_form_other.is_valid(), intake_form_emergency.is_valid(),
#                 intake_form_address.is_valid(), intake_form_email.is_valid(), intake_form_phone.is_valid()]):
#             intake = intake_form.save()
#             contact_id = intake.pk
#             intake_address = intake_form_address.save(commit=False)
#             intake_address.contact_id = contact_id
#             intake_address.save()
#             intake_email = intake_form_email.save(commit=False)
#             intake_email.contact_id = contact_id
#             intake_email.save()
#             intake_phone = intake_form_phone.save(commit=False)
#             intake_phone.contact_id = contact_id
#             intake_phone.save()
#             intake_other = intake_form_other.save(commit=False)
#             intake_other.contact_id = contact_id
#             intake_other.save()
#             intake_emergency = intake_form_emergency.save(commit=False)
#             intake_emergency.contact_id = contact_id
#             intake_emergency.save()
#
#             return HttpResponseRedirect(action)
#         else:
#             print(intake_form.errors, intake_form_other.errors, intake_form_emergency.errors, intake_form_address.errors,
#                   intake_form_email.errors, intake_form_phone.errors)
#
#
#     else:
#         intake_form = IntakeFormContact()
#         intake_form_other = IntakeFormOther()
#         intake_form_address = IntakeFormAddress()
#         intake_form_emergency = IntakeFormEmergency()
#         intake_form_email = IntakeFormEmail()
#         intake_form_phone = IntakeFormPhone()
#
#     return render(request, 'lynx/new_intake_1.html', {'intake_form': intake_form, 'action': action,
#                                                       'intake_form_other': intake_form_other,
#                                                       'intake_form_emergency': intake_form_emergency,
#                                                       'intake_form_address': intake_form_address,
#                                                       'intake_form_email': intake_form_email,
#                                                       'intake_form_phone': intake_form_phone})


@login_required
def add_intake2(request):
    action = "/lynx/add-intake/3/"
    if request.method == 'POST':
        intake_form_history = IntakeFormHistory(request.POST)
        intake_form_criminal = IntakeFormCriminal(request.POST)
        if all([intake_form_criminal.is_valid(),  intake_form_history.is_valid()]):
            intake_criminal = intake_form_criminal.save()
            intake_history = intake_form_history.save()

            return HttpResponseRedirect(action)

    else:
        intake_form_criminal = IntakeFormCriminal()
        intake_form_history = IntakeFormHistory()

    return render(request, 'lynx/new_intake_2.html', {'intake_form_criminal': intake_form_criminal,
                                                      'intake_form_history': intake_form_history, 'action': action})


class ContactListView(LoginRequiredMixin, ListView):

    model = Contact
    paginate_by = 100  # if pagination is desired


class ContactDetailView(LoginRequiredMixin, DetailView):

    model = Contact

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['address_list'] = Address.objects.all()
        context['phone_list'] = Phone.objects.all()
        context['email_list'] = Email.objects.all()
        context['intake_list'] = Intake.objects.all()
        context['referral_list'] = Referral.objects.all()
        context['note_list'] = IntakeNote.objects.all().order_by('-created')
        context['emergency_list'] = EmergencyContact.objects.all()
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
