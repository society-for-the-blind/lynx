from collections import defaultdict
from collections import OrderedDict
from datetime    import datetime, date, timedelta
from urllib.parse import quote
from django      import forms
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins     import LoginRequiredMixin  \
                                         , UserPassesTestMixin

from django.contrib      import messages
from django.contrib.auth import models as dca

from django.core.mail      import send_mail
from django.core.paginator import Paginator
from django.core           import signing

from django.db        import connection
from django.db        import models    as ddm
from django.db.models import functions as ddmf

from django.http          import HttpResponse         \
                               , HttpResponseRedirect \
                               , Http404              \
                               , JsonResponse
from django.shortcuts     import render   \
                               , reverse  \
                               , redirect \
                               , get_object_or_404
from django.urls          import reverse_lazy

# TODO 2025_09_21_1621 Either move to one form or the other
#                      (the `dvg` prefix is not pretty, but
#                       it is explicit)
import django.views.generic as dvg
from django.views.generic import DetailView   \
                               , DeleteView   \
                               , TemplateView \
                               , UpdateView

import csv, logging, os, re, time

# lm  = lynx model
# lfo = lynx forms
# lfi = lynx filter
from . import models  as lm  \
            , forms   as lfo \
            , filters as lfi \
            , kitchen_sink as lks

logger = logging.getLogger(__name__)


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
def authorization_list_view(request, client_id):
    authorizations = lm.Authorization.objects.filter(contact_id=client_id).order_by('-start_date')
    client = lm.Contact.objects.get(id=client_id)
    return render(request, 'lynx/authorization_list.html', {'authorizations': authorizations, 'client': client})

@login_required
def add_intake(request, contact_id):
    form = lfo.IntakeForm()
    if request.method == 'POST':
        form = lfo.IntakeForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/intake/intake_form.html', {'form': form})

@login_required
def add_assignments(request, contact_id):
    form = lfo.AssignmentForm()
    # import pdb; pdb.set_trace()
    instructors = dca.User.objects.filter(groups__name='SIP').order_by(ddmf.Lower('last_name'))
    program_options = lm.Program.objects.filter(is_oib=True).order_by('program')
    assignment_priorities = lm.AssignmentPriority.objects.all().order_by('name')
    assignment_statuses = lm.AssignmentStatus.objects.all().order_by('name')

    if request.method == 'POST':
        form = lfo.AssignmentForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            # assignment_status not shown in form — assign default id 1 explicitly
            form.assignment_status_id = 1
            form.save()

            username = 'SIP Assignments <' + settings.EMAIL_HOST_USER + '>'
            message = "You have a new Assignment by " + request.user.first_name + " with the following note: " + form.note
            instructor = dca.User.objects.filter(pk=form.instructor_id).values('email')
            inst_email = instructor[0]['email']
            client_name = form.contact.first_name + " " + form.contact.last_name

            send_mail(client_name, #subject
                      message, #message
                      username,#from email
                      [inst_email], #recipient list
                      fail_silently=False,
                      )

            return HttpResponseRedirect(reverse('lynx:assignment', args=(contact_id,)))

    return render( request                                          \
                 , 'lynx/add_assignments.html'                      \
                 , { 'form': form                                   \
                   , 'instructors': instructors                     \
                   , 'contact_id': contact_id                       \
                   , 'program_options': program_options             \
                   , 'assignment_priorities': assignment_priorities \
                   , 'assignment_statuses': assignment_statuses     \
                   }                                                \
                 )

@login_required
def add_emergency(request, contact_id):
    form = lfo.EmergencyForm()
    phone_form = lfo.PhoneForm()
    if request.method == 'POST':
        phone_form = lfo.PhoneForm(request.POST)
        form = lfo.EmergencyForm(request.POST)
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

            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_emergency.html',
                  {'phone_form': phone_form, 'form': form})


@login_required
def add_address(request, contact_id):
    form = lfo.AddressForm()
    if request.method == 'POST':
        form = lfo.AddressForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_address.html', {'form': form})


@login_required
def add_email(request, contact_id):
    form = lfo.EmailForm()
    if request.method == 'POST':
        form = lfo.EmailForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_email.html', {'form': form})


@login_required
def add_emergency_email(request, emergency_contact_id):
    form = lfo.EmailForm()
    if request.method == 'POST':
        form = lfo.EmailForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.emergency_contact_id = emergency_contact_id
            form.active = 1
            form.user_id = request.user.id
            form.save()
            emergency = lm.EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_email.html', {'form': form})


@login_required
def add_phone(request, contact_id):
    form = lfo.PhoneForm()
    if request.method == 'POST':
        form = lfo.PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_emergency_phone(request, emergency_contact_id):
    form = lfo.PhoneForm()
    if request.method == 'POST':
        form = lfo.PhoneForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.emergency_contact_id = emergency_contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            emergency = lm.EmergencyContact.objects.get(id=emergency_contact_id)
            contact_id = int(emergency.contact_id)
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_phone.html', {'form': form})


@login_required
def add_authorization(request, contact_id):
    form = lfo.AuthorizationForm()
    if request.method == 'POST':
        form = lfo.AuthorizationForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(form.pk,)))
    return render(request, 'lynx/add_authorization.html', {'form': form})


@login_required
def add_progress_report(request, authorization_id):
    full_name = request.user.first_name + ' ' + request.user.last_name
    current_time = datetime.now()
    current_month = current_time.month
    current_year = current_time.year
    form = lfo.ProgressReportForm(initial={'instructor': full_name, 'month': current_month, 'year': current_year})
    if request.method == 'POST':
        form = lfo.ProgressReportForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = authorization_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(authorization_id,)))
    return render(request, 'lynx/add_progress_report.html', {'form': form})



@login_required
def add_lesson_note(request, authorization_id):
    form = lfo.LessonNoteForm()
    authorization = lm.Authorization.objects.get(id=authorization_id)
    note_list = lm.LessonNote.objects.filter(authorization_id=authorization_id)

    client = lm.Contact.objects.get(id=authorization.contact_id)
    if authorization.authorization_type == 'Hours':
        auth_type = 'individual'
    else:
        auth_type = 'group'
    if request.method == 'POST':
        form = lfo.LessonNoteForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:authorization_detail', args=(authorization_id,)))
    return render(request, 'lynx/add_lesson_note.html', {'form': form, 'client': client, 'auth_type': auth_type,
                                                         'authorization_id': authorization_id})


@login_required
def add_vaccination_record(request, contact_id):
    form = lfo.VaccineForm()
    if request.method == 'POST':
        form = lfo.VaccineForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:contact_show', args=(contact_id,)))
    return render(request, 'lynx/add_vaccine_record.html', {'form': form})


def get_hour_validation(request, authorization_id, billed_units): #check if they are entering more hours then allowed on authorization
    authorization = lm.Authorization.objects.get(id=authorization_id)
    note_list = lm.LessonNote.objects.filter(authorization_id=authorization_id)

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


def get_date_validation(request, authorization_id, note_date): #check if they are entering a lesson note after the authorization authorization
    authorization = lm.Authorization.objects.get(id=authorization_id)
    auth_date = authorization.end_date
    auth_date = auth_date.strftime("%Y-%m-%d")

    if note_date > auth_date:
        return JsonResponse({"result": 'false'})
    else:
        return JsonResponse({"result": 'true'})

@login_required
def contact_search(request):
    query = request.GET.get('query')
    clients = lm.Contact.objects.filter(active=1).order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'))
    if query:
        object_list = lm.Contact.objects.annotate(
            full_name=ddmf.Concat('first_name', ddm.Value(' '), 'last_name')
        ).filter(
            ddm.Q(full_name__icontains=query) |
            ddm.Q(first_name__icontains=query) |
            ddm.Q(last_name__icontains=query)
        )

        object_list = object_list.order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'))
    else:
        object_list = None
    return render(request, 'lynx/contact/contact_search.html', {'object_list': object_list, 'clients': clients})

@login_required
def client_advanced_result_view(request):
    query = request.GET.get('q')
    if query:
        object_list = lm.Contact.objects.annotate(
            full_name=ddmf.Concat('first_name', ddm.Value(' '), 'last_name')
        ).annotate(
            phone_number=ddmf.Replace('phone__phone', ddm.Value('('), ddm.Value(''))
        ).annotate(
            phone_number=ddmf.Replace('phone_number', ddm.Value(')'), ddm.Value(''))
        ).annotate(
            phone_number=ddmf.Replace('phone_number', ddm.Value('-'), ddm.Value(''))
        ).annotate(
            phone_number=ddmf.Replace('phone_number', ddm.Value(' '), ddm.Value(''))
        ).annotate(
            zip_code=ddm.F('address__zip_code')
        ).annotate(
            county=ddm.F('address__county')
        ).annotate(
            intake_date=ddm.F('intake__intake_date')
        ).annotate(
            email_address=ddm.F('email__email')
        ).filter(
            ddm.Q(full_name__icontains=query) |
            ddm.Q(first_name__icontains=query) |
            ddm.Q(last_name__icontains=query) |
            ddm.Q(zip_code__icontains=query) |
            ddm.Q(county__icontains=query) |
            ddm.Q(phone_number__icontains=query) |
            ddm.Q(intake_date__icontains=query) |
            ddm.Q(email_address__icontains=query)
        )

        object_list = object_list.order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'), 'id')
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
        object_list = lm.ProgressReport.objects.filter(month=given_month).filter(
            year=request.GET.get('selYear')).order_by(ddmf.Lower('authorization__contact__last_name'), 'authorization__intake_service_area__agency')

    else:
        object_list = None
        given_month = None
    return render(request, 'lynx/monthly_progress_reports.html', {'object_list': object_list, 'givenMonth': given_month,
                                                                  'givenYear': request.GET.get('selYear')})

class AuthorizationDetailView(LoginRequiredMixin, DetailView):
    model = lm.Authorization

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AuthorizationDetailView, self).get_context_data(**kwargs)
        context['report_list'] = lm.ProgressReport.objects.filter(authorization_id=self.kwargs['pk'])
        context['note_list'] = lm.LessonNote.objects.filter(authorization_id=self.kwargs['pk']).order_by('-date')
        notes = lm.LessonNote.objects.filter(authorization_id=self.kwargs['pk']).values()
        authorization = lm.Authorization.objects.filter(id=self.kwargs['pk']).values()
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
        context['form'] = lfo.LessonNoteForm
        return context

    def post(self, request, *args, **kwargs):
        form = lfo.LessonNoteForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.authorization_id = self.kwargs['pk']
            form.user_id = request.user.id
            form.save()
            # TODO Remove hard coded path (see `SipNoteUpdateView.form_valid`'s return function)
            action = "/lynx/authorization/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)


class ProgressReportDetailView(LoginRequiredMixin, DetailView):
    model = lm.ProgressReport

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgressReportDetailView, self).get_context_data(**kwargs)
        MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7,
                  "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        month_days = {'1': '-01-31', '2': '-02-28', '3': '-03-31', '4': '-04-30', '5': '-05-31', '6': '-06-30',
                      '7': '-07-31', '8': '-08-31', '9':'-09-30', '10': '-10-31', '11':'-11-30', '12': '-12-31'}

        report = lm.ProgressReport.objects.filter(id=self.kwargs['pk']).values()
        auth_id = report[0]['authorization_id']
        month_number = report[0]['month']
        year = report[0]['year']
        if len(month_number) > 2:
            month = report[0]['month']
            month_number = MONTHS[month]
        max_date = str(year) + month_days[month_number]
        notes = lm.LessonNote.objects.filter(authorization_id=auth_id).filter(
            date__month=month_number).filter(date__year=year).values()
        all_notes = lm.LessonNote.objects.filter(authorization_id=auth_id).filter(date__lte=max_date).values()
        authorization = lm.Authorization.objects.filter(id=auth_id).values()

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
    model = lm.LessonNote


class BillingReviewDetailView(LoginRequiredMixin, DetailView):
    model = lm.Authorization
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
        # report = lm.ProgressReport.objects.filter(authorization_id=auth_id).values()
        notes = lm.LessonNote.objects.filter(authorization_id=auth_id).filter(date__month=month).filter(date__year=year).order_by(
            'date').values()
        reports = lm.ProgressReport.objects.filter(authorization_id=auth_id).values()
        month_report = lm.ProgressReport.objects.filter(authorization_id=auth_id).filter(month=month).filter(year=year).values()[:1]
        context['month_report'] = month_report
        authorization = lm.Authorization.objects.filter(id=auth_id).values()

        context['note_list'] = notes

        contact_id = authorization[0]['outside_agency_id']
        outside = lm.Contact.objects.filter(id=contact_id).values()
        context['payment'] = outside[0]['first_name'] + ' ' + outside[0]['last_name'] + ' - ' + outside[0]['company']
        # contact_id = outside[0]['contact_id']
        address = lm.Address.objects.filter(contact_id=contact_id).values()[:1]
        context['address'] = address
        phone = lm.Phone.objects.filter(contact_id=contact_id).values()[:1]
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

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = lm.Contact
    template_name = 'lynx/contact/contact_show.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        intake = self.object.intake_set.exclude(birth_date__isnull=True).order_by('-intake_date').first()
        age = None
        if intake and intake.birth_date:
            today = date.today()
            birth_date = intake.birth_date
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        context['client_age'] = age
        context['program_memberships'] = lm.ContactProgram.objects.filter(
                contact_id=self.kwargs['pk'],
                end_date__isnull=True
            ).select_related('program')
        context['address_list'] = lm.Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = lm.Phone.objects.filter(contact_id=self.kwargs['pk']).order_by('created')
        context['email_list'] = lm.Email.objects.filter(contact_id=self.kwargs['pk'])
        context['intake_list'] = lm.Intake.objects.filter(contact_id=self.kwargs['pk'])
        context['authorization_list'] = lm.Authorization.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['note_list'] = lm.IntakeNote.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['emergency_list'] = lm.EmergencyContact.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['document_list'] = lm.Document.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['vaccine_list'] = lm.Vaccine.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['instructor_list'] = lm.Assignment.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['form'] = lfo.IntakeNoteForm
        context['upload_form'] = lfo.DocumentForm

        oib_plans = _get_plans(self.object)
        oib_programs = sorted(list({plan['program'] for plan in oib_plans}))
        context['oib_programs'] = oib_programs
        # import pdb; pdb.set_trace()

        # add historical SIP / ILP existence flag and counts
        client_id = self.kwargs['pk']

        # compute warnings / optionally auto-end offending memberships
        birth_date = intake.birth_date if intake else None
        violations = lks.program_age_violations(self.object, birth_date)

        # If violations found and user requested auto-end (or is superuser) end memberships now
        # Trigger by ?auto_end=1 or always for superusers
        auto_end_requested = self.request.GET.get('auto_end') == '1' or self.request.user.is_superuser

        if violations and auto_end_requested:
            violating_program_codes = {v['program'] for v in violations}
            today = date.today()
            # get queryset of offending active memberships
            memberships_qs = (
                self.object.contactprogram_set
                .filter(end_date__isnull=True, program__program__in=violating_program_codes)
                .select_related('program')
            )
            # capture program names before the update (query will no longer match after update)
            program_names = list(memberships_qs.values_list('program__program', flat=True))
            # bulk update end_date to avoid triggering model.full_clean()
            updated_count = memberships_qs.update(end_date=today)
            ended = program_names if updated_count else []
            # refresh program_memberships to reflect ended rows
            context['program_memberships'] = lm.ContactProgram.objects.filter(
                contact_id=self.kwargs['pk'],
                end_date__isnull=True
            ).select_related('program')
            # surface a user-visible message
            if ended:
                messages.warning(
                    self.request,
                    "Automatically ended program membership(s) due to DOB / age mismatch: " + ", ".join(ended)
                )
            # keep a record in template context as well
            context['program_age_autoended'] = ended

        return context

    # TODO Potentially unsafe; handle uploads and new notes explicitly, refuse anything else.
    def post(self, request, *args, **kwargs):
        if 'note' in request.POST:
            form = lfo.IntakeNoteForm(request.POST, request.FILES)
            upload = False
        else:
            form = lfo.DocumentForm(request.POST, request.FILES)
            upload = True

        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = self.kwargs['pk']
            form.user_id = request.user.id
            if upload:
                form.description = request.FILES['document'].name
            form.save()
            # TODO Remove hard coded path (see `SipNoteUpdateView.form_valid`'s return function)
            action = "/lynx/clients/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)

class ContactFormView(LoginRequiredMixin, dvg.edit.ModelFormMixin):
    model = lm.Contact
    form_class = lfo.ContactForm
    template_name = 'lynx/contact/contact_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact = getattr(self, 'object', None)
        context['address_form'] = lfo.AddressForm(instance=getattr(contact, 'address_set', None).first() \
                                  if contact else None)
        context['phone_form'] = lfo.PhoneForm(instance=getattr(contact, 'phone_set', None).first() \
                                if contact else None)
        context['email_form'] = lfo.EmailForm(instance=getattr(contact, 'email_set', None).first() \
                                if contact else None)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.id
        self.object.save()
        contact_id = self.object.pk

        # Save related forms
        address_form = lfo.AddressForm(self.request.POST)
        phone_form = lfo.PhoneForm(self.request.POST)
        email_form = lfo.EmailForm(self.request.POST)
        if address_form.is_valid() and address_form.cleaned_data.get('address_one'):
            address = address_form.save(commit=False)
            address.contact_id = contact_id
            address.user_id = self.request.user.id
            address.save()
        if phone_form.is_valid() and phone_form.cleaned_data.get('phone'):
            phone = phone_form.save(commit=False)
            phone.contact_id = contact_id
            phone.user_id = self.request.user.id
            phone.active = True
            phone.save()
        if email_form.is_valid() and email_form.cleaned_data.get('email'):
            email = email_form.save(commit=False)
            email.contact_id = contact_id
            email.user_id = self.request.user.id
            email.active = True
            email.save()

        return HttpResponseRedirect(reverse('lynx:add_emergency', args=(contact_id,)))

# For add
class ContactCreateView(ContactFormView, dvg.CreateView):
    pass

# For update
class ContactUpdateView(ContactFormView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop('address_form', None)
        context.pop('phone_form', None)
        context.pop('email_form', None)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.id
        self.object.save()
        contact = self.object

        selected_programs = set(form.cleaned_data.get('programs', []))
        # Find all active memberships
        active_memberships = list(contact.contactprogram_set.filter(end_date__isnull=True))

        # End memberships for unchecked programs
        for cp in active_memberships:
            if cp.program not in selected_programs:
                cp.end_date = date.today()
                cp.save()

        # Start memberships for newly checked programs
        # Only create if there is NO active membership for this program
        active_programs = set(cp.program for cp in active_memberships if cp.end_date is None)
        for program in selected_programs:
            if program not in active_programs:
                lm.ContactProgram.objects.create(
                    contact=contact,
                    program=program,
                    start_date=date.today(),
                    end_date=None
                )

        return HttpResponseRedirect(reverse('lynx:contact_show', args=(self.object.pk,)))

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Address
    fields = ['address_one', 'address_two', 'suite', 'city', 'state', 'zip_code', 'county', 'country', 'region',
              'cross_streets', 'bad_address', 'address_notes', 'preferred_medium']
    template_name_suffix = '_edit'


class EmailUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Email
    fields = ['email', 'email_type', 'active']
    template_name_suffix = '_edit'


class PhoneUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Phone
    fields = ['phone', 'phone_type', 'active']
    template_name_suffix = '_edit'

class IntakeUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Intake
    template_name = 'lynx/intake/intake_form.html'
    fields = ['intake_date', 'intake_type', 'gender', 'pronouns', 'birth_date', 'ethnicity',
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

    confirm_flag = 'confirm_birth_date_change'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["intake_date"].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields["birth_date"].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields["eye_condition_date"].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields["hire_date"].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields["other_languages"].label = "Other Language(s)"
        form.fields["ethnicity"].label = "Race"
        form.fields["other_ethnicity"].label = "Ethnicity"
        form.fields['payment_source'].queryset = lm.Contact.objects.filter(payment_source=1).order_by(ddmf.Lower('last_name'))
        form.fields['payment_source'].label = "Payment Sources"
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

    def _program_age_violations(self, contact, proposed_birth_date):
        # keep method for compatibility with existing callsites;
        # return same shape as older implementation (list of tuples) so
        # existing code that destructures (p, req, age) keeps working.
        dicts = lks.program_age_violations(contact, proposed_birth_date)
        return [(d['program'], d['requirements'], d['age_on_start']) for d in dicts]

    def form_valid(self, form):
        db_obj = self.get_object()
        old_birth_date = db_obj.birth_date
        new_birth_date = form.cleaned_data.get('birth_date')
        session_key = f"pending_birth_date_change_{db_obj.pk}"

        # Build instance but do not persist yet
        intake = form.save(commit=False)

        if new_birth_date != old_birth_date:
            violations = self._program_age_violations(db_obj.contact, new_birth_date)
            if violations:
                # Save all other edits, keep old DOB
                intake.birth_date = old_birth_date
                intake.save()
                # Save session payload
                self.request.session[session_key] = {
                    'new_birth_date': new_birth_date.isoformat(),
                    'violations': [
                        {'program': p, 'requirements': req, 'age_on_start': age}
                        for (p, req, age) in violations
                    ]
                }
                self.request.session.modified = True
                return redirect('lynx:intake_birthdate_confirm', pk=db_obj.pk)
        # No violations or DOB unchanged: save normally (includes new DOB)
        intake.save()
        return HttpResponseRedirect(intake.get_absolute_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class IntakeBirthDateConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'lynx/intake/intake_birthdate_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intake = get_object_or_404(lm.Intake, pk=self.kwargs['pk'])
        session_key = f"pending_birth_date_change_{intake.pk}"
        pending = self.request.session.get(session_key)
        if not pending:
            context['invalid'] = True
            return context
        context.update({
            'intake': intake,
            'contact': intake.contact,
            'new_birth_date': pending['new_birth_date'],
            'violations': pending['violations'],
            'today': date.today(),
        })
        return context

    def post(self, request, *args, **kwargs):
        intake = get_object_or_404(lm.Intake, pk=kwargs['pk'])
        session_key = f"pending_birth_date_change_{intake.pk}"
        pending = request.session.get(session_key)
        if not pending:
            return redirect('lynx:intake_edit', pk=intake.pk)

        action = request.POST.get('action')
        if action == 'cancel':
            # User cancelled: DOB stays old; other edits already saved.
            # Clear the pending session payload and return to the client detail view.
            request.session.pop(session_key, None)
            return redirect('lynx:contact_show', pk=intake.contact_id)

        if action == 'confirm':
            new_birth_date = date.fromisoformat(pending['new_birth_date'])
            violating_program_codes = {v['program'] for v in pending['violations']}
            today = date.today()
            memberships = (
                intake.contact.contactprogram_set
                .filter(end_date__isnull=True, program__program__in=violating_program_codes)
                .select_related('program')
            )
            # Bulk end offending memberships to avoid running model.full_clean() on each instance
            memberships_qs = (
                intake.contact.contactprogram_set
                .filter(end_date__isnull=True, program__program__in=violating_program_codes)
                .select_related('program')
            )
            program_names = list(memberships_qs.values_list('program__program', flat=True))
            updated_count = memberships_qs.update(end_date=today)
            if updated_count:
                messages.warning(
                    request,
                    "Automatically ended program membership(s) due to DOB / age mismatch: " + ", ".join(program_names)
                )

            intake.birth_date = new_birth_date
            lm.Intake.objects.filter(pk=intake.pk).update(birth_date=new_birth_date)

            request.session.pop(session_key, None)
            return redirect('lynx:contact_show', pk=intake.contact_id)

        return redirect('lynx:intake_edit', pk=intake.pk)

class IntakeNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.IntakeNote
    fields = ['note']
    template_name_suffix = '_edit'


class EmergencyContactUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.EmergencyContact
    fields = ['name',  'emergency_notes', 'relationship']
    template_name_suffix = '_edit'


class LessonNoteUpdateView(LoginRequiredMixin, UpdateView):
    form_class = lfo.LessonNoteForm
    model = lm.LessonNote
    template_name_suffix = '_edit'


class ProgressReportUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.ProgressReport
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
        form.fields["short_term_goals_time"].label = "Estimated number of Hours needed for completion of short term objectives"
        form.fields["long_term_goals"].label = "Remaining Long Term Objectives"
        form.fields["long_term_goals_time"].label = "Estimated number of Hours needed for completion of long term objectives"
        return form

class AuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Authorization
    fields = ['intake_service_area', 'authorization_number', 'authorization_type', 'start_date', 'end_date',
              'total_time', 'billing_rate', 'outside_agency', 'student_plan', 'notes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['start_date'].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields['end_date'].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields['outside_agency'].queryset = lm.Contact.objects.filter(payment_source=1).order_by(ddmf.Lower('last_name'))
        form.fields['outside_agency'].label = "Payment Sources"
        form.fields['start_date'].label = "Start Date (YYYY-MM-DD)"
        form.fields['end_date'].label = "End Date (YYYY-MM-DD)"
        return form

class VaccineUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Vaccine
    fields = ['vaccine', 'vaccine_note', 'vaccination_date']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['vaccination_date'].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields['vaccine'].label = "Type"
        form.fields['vaccine_note'].label = "Notes"
        form.fields['vaccination_date'].label = "Date"
        return form


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Assignment
    fields = ['program', 'priority', 'note']
    template_name_suffix = '_edit'

    def get_success_url(self):
        return self.request.GET.get('next')


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Assignment

    def get_success_url(self):
        return self.request.GET.get('next')

class IntakeNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.IntakeNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_show', kwargs={'pk': client_id})


class ProgressReportDeleteView(UserPassesTestMixin, DeleteView):
    model = lm.ProgressReport

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class AuthorizationDeleteView(UserPassesTestMixin, DeleteView):
    model = lm.Authorization

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_show', kwargs={'pk': client_id})


class ContactDeleteView(UserPassesTestMixin, DeleteView):
    model = lm.Contact
    template_name = 'lynx/contact/contact_confirm_delete.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('lynx:index')


class LessonNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.LessonNote

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class PhoneDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Phone

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_show', kwargs={'pk': client_id})


class VaccineDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Vaccine

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_show', kwargs={'pk': client_id})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Document

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:contact_show', kwargs={'pk': client_id})


@login_required
def billing_report(request):
    form = lfo.BillingReportForm()
    if request.method == 'POST':
        form = lfo.BillingReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            month = data.get('month')
            year = data.get('year')

            if month == 'all':
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area,
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.first_name, ' ', oa.last_name, ' - ',
                                        oa.company) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_contact as oa on auth.outside_agency_id = oa.id
                                        where extract(year FROM date) = '%s'
                                        order by c.last_name, c.first_name, sa.agency;""" % (year,))
                    auth_set = dictfetchall(cursor)
            else:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CONCAT(c.first_name, ' ', c.last_name) as name, sa.agency as service_area,
                                        auth.authorization_type, auth.authorization_number, auth.id as authorization_id,
                                        ln.billed_units, auth.billing_rate, CONCAT(oa.first_name, ' ', oa.last_name, ' - ',
                                        oa.company) as outside_agency
                                        FROM lynx_authorization as auth
                                        LEFT JOIN lynx_contact as c on c.id = auth.contact_id
                                        LEFT JOIN lynx_lessonnote as ln  on ln.authorization_id = auth.id
                                        LEFT JOIN lynx_intakeservicearea as sa on auth.intake_service_area_id = sa.id
                                        LEFT JOIN lynx_contact as oa on auth.outside_agency_id = oa.id
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
    form = lfo.SipDemographicReportForm()
    if request.method == 'POST':
        form = lfo.SipDemographicReportForm(request.POST)
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

            # --- REWRITE: Use Program.program for SIP membership ---
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, int.intake_date as date, int.age_group, int.gender, int.ethnicity,
                        int.degree, int.eye_condition, int.eye_condition_date, int.education, int.living_arrangement, int.residence_type,
                        int.dialysis, int.stroke, int.seizure, int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma,
                        int.cancer, int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse, int.memory_loss,
                        int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.referred_by, int.hearing_loss,
                        c.first_name, c.last_name, int.birth_date
                    FROM lynx_sipnote ls
                    LEFT JOIN lynx_contact as c  ON c.id = ls.contact_id
                    LEFT JOIN lynx_intake as int  ON int.contact_id = c.id
                    WHERE c.id != 111
                      AND extract(month FROM ls.note_date) = %s
                      AND extract(year FROM ls.note_date) = '%s'
                      AND EXISTS (
                          SELECT 1
                          FROM lynx_contactprogram cp
                          JOIN lynx_program p ON cp.program_id = p.id
                          WHERE cp.contact_id = c.id
                            AND p.program = 'SIP'
                            AND (cp.end_date IS NULL OR cp.end_date > ls.note_date)
                            AND cp.start_date <= ls.note_date
                      )
                      %s
                    ORDER BY c.last_name, c.first_name;
                """ % (month, year, month_string))
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
    form = lfo.SipCSFReportForm()
    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_services_report(request):
    form = lfo.SipCSFReportForm()
    if request.method == 'POST':
        form = lfo.SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                query = """
                    SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, ls.fiscal_year,
                        ls.vision_screening, ls.treatment, ls.at_devices, ls.at_services, ls.orientation, ls.communications,
                        ls.dls, ls.support, ls.advocacy, ls.counseling, ls.information, ls.services, addr.county, ls.note_date,
                        ls.independent_living, sp.living_plan_progress, sp.community_plan_progress, sp.ila_outcomes,
                        sp.at_outcomes, ls.class_hours
                    FROM lynx_sipnote as ls
                    LEFT JOIN lynx_contact as c on c.id = ls.contact_id
                    INNER JOIN lynx_address as addr on c.id = addr.contact_id
                    LEFT JOIN lynx_sipplan as sp on sp.id = ls.sip_plan_id
                    WHERE fiscal_year = '%s'
                      AND quarter <= %d
                      AND EXISTS (
                          SELECT 1
                          FROM lynx_contactprogram cp
                          JOIN lynx_program p ON cp.program_id = p.id
                          WHERE cp.contact_id = c.id
                            AND p.program = 'SIP'
                            AND (cp.end_date IS NULL OR cp.end_date > ls.note_date)
                            AND cp.start_date <= ls.note_date
                      )
                    ORDER BY c.last_name, c.first_name;
                """ % (fiscal_year, int(quarter))
                cursor.execute(query)
                note_set = dictfetchall(cursor)

            # ...rest of your CSV writing code remains unchanged...
            # (no changes needed below this line)
            filename = "SIP Quarterly Services Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            # ...etc...
            # (rest of your code unchanged)
            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


@login_required
def sip_csf_demographic_report(request):
    form = lfo.SipCSFReportForm()
    if request.method == 'POST':
        form = lfo.SipCSFReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            quarter = data.get('quarter')
            year = data.get('year')
            fiscal_year = get_fiscal_year(year)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, int.age_group,
                        int.gender, int.ethnicity, int.degree, int.eye_condition, int.eye_condition_date, int.education,
                        int.living_arrangement, int.residence_type, addr.county, int.dialysis, int.stroke, int.seizure,
                        int.heart, int.arthritis, int.high_bp, int.neuropathy, int.pain, int.asthma, int.cancer,
                        int.musculoskeletal, int.alzheimers, int.allergies, int.mental_health, int.substance_abuse,
                        int.memory_loss, int.learning_disability, int.geriatric, int.dexterity, int.migraine, int.hearing_loss,
                        int.referred_by, ls.note_date, int.communication, int.other_ethnicity
                    FROM lynx_sipnote as ls
                    LEFT JOIN lynx_contact as c on c.id = ls.contact_id
                    LEFT JOIN lynx_intake as int on int.contact_id = c.id
                    INNER JOIN lynx_address as addr on c.id = addr.contact_id
                    WHERE fiscal_year = '%s'
                      AND quarter = %d
                      AND EXISTS (
                          SELECT 1
                          FROM lynx_contactprogram cp
                          JOIN lynx_program p ON cp.program_id = p.id
                          WHERE cp.contact_id = c.id
                            AND p.program = 'SIP'
                            AND (cp.end_date IS NULL OR cp.end_date > ls.note_date)
                            AND cp.start_date <= ls.note_date
                      )
                      AND c.id NOT IN (
                          SELECT contact_id FROM lynx_sipnote AS sip
                          WHERE quarter < %d AND fiscal_year = '%s'
                      )
                    ORDER BY c.last_name, c.first_name;
                """ % (fiscal_year, int(quarter), int(quarter), fiscal_year))
                client_set = dictfetchall(cursor)

            # ...rest of your CSV writing code remains unchanged...
            filename = "SIP Quarterly Demographic Report - Q" + str(quarter) + " - " + str(fiscal_year)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(response)
            # ...etc...
            # (rest of your code unchanged)
            return response

    return render(request, 'lynx/sip_quarterly_report.html', {'form': form})


def units_to_hours(units):
    minutes = units * 15
    hours = minutes / 60
    return hours

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

@login_required
def contact_filter(request):
    """
    Filter Contacts by intake dates, age group, email/county/phone substrings,
    active flag and program membership.
    """
    # default intake_after -> current grant year start
    if request.GET:
        f = lfi.ContactFilter(request.GET, queryset=lm.Contact.objects.all().order_by('last_name', 'first_name'))
    else:
        initial = {
            'intake_after': grant_year_start_date(),
            'is_active': True,
        }
        f = lfi.ContactFilter(initial, queryset=lm.Contact.objects.all().order_by('last_name', 'first_name'))

    # annotate/prefetch to reduce per-row queries in template
    qs = f.qs.select_related().prefetch_related('programs', 'email_set', 'address_set', 'phone_set').distinct()

    # build condensed results for simple template consumption (optional)
    clients = []
    for c in qs:
        clients.append({
            'id': c.id,
            'full_name': f"{c.last_name}, {c.first_name}",
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email_set.first().email if c.email_set.exists() else '',
            'phone': c.phone_set.first().phone if c.phone_set.exists() else '',
            'county': c.address_set.first().county if c.address_set.exists() else '',
            'active': c.active,
            'programs': ", ".join([p.program for p in c.programs.all()]),
        })

    return render(request, 'lynx/contact/contact_filter.html', {
        'filter': f,
        'clients': clients,
    })

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

def grant_year_start_date():
    grant_start_month = 10  # October
    grant_start_day = 1
    today = date.today()
    if today.month >= grant_start_month:
        start_date = date(today.year, grant_start_month, grant_start_day)
    else:
        start_date = date(today.year - 1, grant_start_month, grant_start_day)
    return start_date

@login_required
def oib_assignment_list(request):
    # import pdb; pdb.set_trace()
    if request.method == 'GET':
        strict = True

        # The assignment  filter form  gets submitted  via GET
        # method, but the first  assignments page load is also
        # a  GET (naturally),  so to  set a  default date  for
        # "Assignments  after date"  the  form submission  and
        # initial page load have to  be discerned: if the page
        # load input  (i.e., `requet.GET`) is empty,  then the
        # page is being loaded the first time.
        if request.GET:
            f = lfi.AssignmentFilter(request.GET, queryset=lm.Assignment.objects.all().order_by('-assignment_date'))
        else:
            initial_data = {
                'assignment_date_gt': grant_year_start_date()
            ,   'instructor': request.user.id
            }
            f = lfi.AssignmentFilter(initial_data, queryset=lm.Assignment.objects.all().order_by('-assignment_date'))

        assignment_condensed = {}
        for assignment in f.qs:
            assignment_condensed[assignment.id] = {}

            program_code = getattr(assignment.program, 'program', '') if assignment.program else ''
            assignment_condensed[assignment.id]['program'] = program_code

            assignment_condensed[assignment.id]['assignment_id'] = assignment.id if assignment.id is not None else ''
            assignment_condensed[assignment.id]['assignment_date'] = assignment.assignment_date if assignment.assignment_date is not None else ''
            assignment_condensed[assignment.id]['timestamp'] = timestamp = int(time.mktime(assignment.assignment_date.timetuple())) if assignment.assignment_date is not None else ''
            assignment_condensed[assignment.id]['assignment_priority'] = getattr(assignment.priority, 'name', '') if assignment.priority else ''
            assignment_condensed[assignment.id]['client_id'] = assignment.contact_id if assignment.contact_id is not None else ''
            assignment_condensed[assignment.id]['client_first_name'] = assignment.contact.first_name if assignment.contact.first_name is not None else ''
            assignment_condensed[assignment.id]['client_last_name'] = assignment.contact.last_name if assignment.contact.last_name is not None else ''
            assignment_condensed[assignment.id]['note'] = assignment.note if assignment.note is not None else ''
            assignment_condensed[assignment.id]['assigned_by_first_name'] = assignment.user.first_name if assignment.user.first_name is not None else ''
            assignment_condensed[assignment.id]['assigned_by_last_name'] = assignment.user.last_name if assignment.user.last_name is not None else ''
            # assignment_condensed[assignment.id]['assignment_status'] = assignment.assignment_status if assignment.assignment_status is not None else ''
            assignment_condensed[assignment.id]['instructor_first_name'] = assignment.instructor.first_name if assignment.instructor.first_name is not None else ''
            assignment_condensed[assignment.id]['instructor_last_name'] = assignment.instructor.last_name if assignment.instructor.last_name is not None else ''

            most_recent_in_home_service_event = (
                lm.OIBServiceEvent.objects
                .filter(
                    contacts__id=assignment.contact_id,
                    oib_service_delivery_type__oib_service_delivery_type__iexact='In-home'
                )
                .select_related('oib_service_delivery_type')  # keep FK joins
                .prefetch_related(
                    # Prefetch the through-model so we also have role info if needed
                    ddm.Prefetch(
                        'oibserviceeventinstructor_set',
                        queryset=lm.OIBServiceEventInstructor.objects.select_related('instructor', 'oib_service_event_instructor_role'),
                        to_attr='instructor_roles'
                    )
                    # alternatively: .prefetch_related('instructors') to get User instances only
                )
                .order_by('-date', '-id')
                .first()
            )

            if most_recent_in_home_service_event:
                mrihse = most_recent_in_home_service_event
                assignment_condensed[assignment.id]['most_recent_in_home_note_id']         = mrihse.id
                assignment_condensed[assignment.id]['most_recent_in_home_note_date']       = mrihse.date
                assignment_condensed[assignment.id]['most_recent_in_home_note']            = mrihse.note
                instructors = [ir.instructor for ir in getattr(mrihse, 'instructor_roles', [])]
                instructor_names = [f"{u.first_name} {u.last_name}".strip() for u in instructors]
                assignment_condensed[assignment.id]['most_recent_in_home_note_instructor'] = ", ".join(instructor_names) if instructor_names else 'n/a'
            else:
                assignment_condensed[assignment.id]['most_recent_in_home_note_id']         = ''
                assignment_condensed[assignment.id]['most_recent_in_home_note_date']       = ''
                assignment_condensed[assignment.id]['most_recent_in_home_note']            = ''
                assignment_condensed[assignment.id]['most_recent_in_home_note_instructor'] = ''

            # ==========================================================

            intakenotes = getattr(assignment.contact, 'related_intakenotes', [])
            # Again, same as above, but got burned by this form a couple times
            # intakenotes = assignment.contact.related_intakenotes

            client_notes_for_assignee = [
                note for note in intakenotes
                if      note.user_id == assignment.instructor_id
                    and note.created.date() >= assignment.assignment_date
            ]

            if client_notes_for_assignee:
                # If there are any intake notes, add the date and note of the most recent one
                most_recent_client_note_by_assignee = max(client_notes_for_assignee, key=lambda note: note.modified)
                cn = most_recent_client_note_by_assignee
                # import pdb; pdb.set_trace()
                assignment_condensed[assignment.id]['intakenote_date'] = cn.modified.date()
                assignment_condensed[assignment.id]['intakenote'] = cn.note

                if cn.user:
                    assignment_condensed[assignment.id]['intakenote_instructor'] = f'{cn.user.first_name} {cn.user.last_name}'
                else:
                    assignment_condensed[assignment.id]['intakenote_instructor'] = 'n/a'

            else:
                # If there are no intake notes, add empty values
                assignment_condensed[assignment.id]['intakenote_date'] = ''
                assignment_condensed[assignment.id]['intakenote'] = ''

    else:
        f = lfi.AssignmentFilter()
        assignment_condensed = {}

    return render(request, 'lynx/assignment_list.html', {'filter': f, 'assignment_list': assignment_condensed})

@login_required
def oib_assignment_list_for_client(request, contact_id):
    instructor_list = lm.Assignment.objects.filter(contact_id=contact_id).order_by('-assignment_date')
    # contact = lm.Contact.objects.get(id=contact_id).first()
    contact = lm.Contact.objects.filter(pk=contact_id).first()
    # import pdb; pdb.set_trace()
    return render(request, 'lynx/assignment_detail.html', {'instructor_list': instructor_list, "contact_id": contact_id, 'contact': contact})

####################################################
# OIB RE-WRITE                                     #
####################################################

# SERVICE EVENTS (aka notes)
@login_required
def oib_service_event_show(request, oib_service_event_id):
    service_event = \
        get_object_or_404(lm.OIBServiceEvent, pk=oib_service_event_id)
    instructors_with_roles = (
        lm.OIBServiceEventInstructor
        .objects
        .select_related('instructor', 'oib_service_event_instructor_role')
        .filter(oib_service_event=service_event)
    )
    return render( request
                 , 'lynx/oib/oib_service_event_show.html'
                 , { 'service_event': service_event
                   , 'instructors_with_roles': instructors_with_roles
                   }
                 )

@login_required
def oib_service_event_delete(request, oib_service_event_id):

    service_event = get_object_or_404(lm.OIBServiceEvent, pk=oib_service_event_id)
    contact = service_event.contacts.first()
    contact_id = contact.id if contact else 1

    if request.method == "POST":
        lm.OIBServiceEventInstructor.objects.filter(oib_service_event=service_event).delete()
        lm.OIBServiceEventContact.objects.filter(oib_service_event=service_event).delete()
        lm.OIBServiceEventOIBService.objects.filter(oib_service_event=service_event).delete()
        service_event.delete()

        return redirect( 'lynx:oib_service_event_list')
    return render( request \
                 , "lynx/oib/oib_service_event_confirm_delete.html" \
                 , {"service_event": service_event} \
                 )

@login_required
def oib_service_event_list(request):
    today = date.today()
    initial = {'start_date': today, 'end_date': today}

    if request.GET:
        form = lfo.OIBServiceEventFilterForm(request.GET)
        qs = lm.OIBServiceEvent.objects.none()
        highlight_tokens = []
        if form.is_valid():
            cd = form.cleaned_data
            # consider the form "active" only when at least one filter value is present
            any_filter = any([
                bool((cd.get('client') or '').strip()),
                bool(cd.get('program')),
                bool(cd.get('service_delivery_type')),
                bool(cd.get('entered_by')),
                bool(cd.get('start_date')),
                bool(cd.get('end_date')),
                bool((cd.get('keyword') or '').strip()),
            ])
            if any_filter:
                qs = lm.OIBServiceEvent.objects.select_related(
                    "oib_service_delivery_type",
                    "entered_by"
                ).prefetch_related(
                    "contacts",
                    "instructors"
                ).order_by("-date", "-id")

                client_q = (cd.get('client') or '').strip()
                if client_q:
                    # tokenise client query and filter (existing logic)
                    tokens = [t for t in re.split(r'\s+', client_q) if t]
                    q_obj = None
                    for tok in tokens:
                        cond = ddm.Q(contacts__last_name__icontains=tok) | ddm.Q(contacts__first_name__icontains=tok)
                        q_obj = cond if q_obj is None else (q_obj & cond)
                    if q_obj is not None:
                        qs = qs.filter(q_obj)
                    highlight_tokens.extend(tokens)

                kw = (cd.get('keyword') or '').strip()
                if kw:
                    # filter notes (existing logic)
                    qs = qs.filter(note__icontains=kw)
                    # also include keyword tokens for highlighting
                    highlight_tokens.extend([t for t in re.split(r'\s+', kw) if t])

                sdt = cd.get('service_delivery_type')
                if sdt:
                    qs = qs.filter(oib_service_delivery_type=sdt)

                instructor = cd.get('instructor')
                if instructor:
                    qs = qs.filter(instructors=instructor)

                entered_by = cd.get('entered_by')
                if entered_by:
                    qs = qs.filter(entered_by=entered_by)

                start = cd.get('start_date')
                end = cd.get('end_date')
                # Validate date range: only run DB query when range is valid.
                if start and end and start > end:
                    # attach a non-field error so the template can show it via form.non_field_errors
                    form.add_error(None, "Start date cannot be later than end date.")
                    qs = lm.OIBServiceEvent.objects.none()
                else:
                    if start:
                        qs = qs.filter(date__gte=start)
                    if end:
                        qs = qs.filter(date__lte=end)

        # avoid duplicates because of M2M joins
        qs = qs.distinct()
    else:
        # initial page load: show filter form prefilled (start/end default to today)
        form = lfo.OIBServiceEventFilterForm(initial=initial)
        qs = lm.OIBServiceEvent.objects.none()
        highlight_tokens = []

    return render(
        request,
        "lynx/oib/oib_service_event_list.html",
        {
            "form": form,
            "service_events": qs,
            "page_title": "SIP/ILP Group Notes",
            "highlight_tokens": highlight_tokens,
        },
    )

# TODO This should be in a utility module
def parse_duration_string(s):
    h, m, sec = map(int, s.split(":"))
    return timedelta(hours=h, minutes=m, seconds=sec)

@login_required
def active_oib_clients(request):
    """
    Return HTML <option> items for client selects.
    GET params:
      - q: optional text to filter (first/last) - inactive for now
      - selected: optional id to include selected at top
    """
    # q = (request.GET.get('q') or '').strip()
    selected = request.GET.get('selected')
    qs = lm.Contact.active_oib_qs()
    # if q:
    #     qs = qs.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q))
    # qs = qs[:100]  # limit to avoid huge responses

    parts = []
    # Ensure selected appears first (if provided)
    if selected:
        try:
            sel = lm.Contact.objects.get(pk=selected)
            parts.append(f'<option value="{sel.pk}">{sel.last_name}, {sel.first_name}</option>')
        except lm.Contact.DoesNotExist:
            pass

    for c in qs:
        if selected and str(c.pk) == str(selected):
            continue
        parts.append(f'<option value="{c.pk}">{c.last_name}, {c.first_name}</option>')

    return HttpResponse('\n'.join(parts), content_type='text/html')

@login_required
def oib_service_event_form(request, oib_service_event_id=None):
    """Unified view for both adding and editing OIB service events."""
    edit_mode = oib_service_event_id is not None
    template_path = "lynx/oib/oib_service_event_add.html"

    # Set up formsets
    OIBServiceEventUserRoleFormSet = forms.formset_factory(
        lfo.OIBServiceEventUserRoleForm,
        extra=0,
        can_delete=True,
        min_num=1,
        validate_min=True
    )
    user_role_form_prefix = 'user_role'

    OIBServiceEventContactFormSet = forms.formset_factory(
        lfo.OIBServiceEventContactForm,
        extra=0,
        can_delete=True,
        min_num=1,
        validate_min=True
    )
    client_form_prefix = 'client'

    # For edit mode, fetch the existing service event
    service_event = None
    initial_data = {}
    user_role_initial = []
    client_initial = []

    if edit_mode:
        service_event = get_object_or_404(lm.OIBServiceEvent, pk=oib_service_event_id)

        def _timedelta_to_hms(td):
            if not td:
                return None
            total_seconds = int(td.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        initial_data = {
            'plan_type': service_event.oib_service_delivery_type.pk,
            'note_date': service_event.date,
            'event_length': _timedelta_to_hms(service_event.length),
            'services': [s.oib_service.pk for s in service_event.oibserviceeventoibservice_set.all()],
            'note': service_event.note,
        }
        user_role_initial = [
            {
                'instructor': osei.instructor,
                'role': osei.oib_service_event_instructor_role,
            }
            for osei in lm.OIBServiceEventInstructor.objects.filter(oib_service_event=service_event)
        ]
        client_initial = [
            {
                'client': osec.contact,
            }
            for osec in lm.OIBServiceEventContact.objects.filter(oib_service_event=service_event)
        ]

    def _attach_client_htmx_attrs(formset):
        """Attach HTMX attrs to client selects in a formset (called before rendering)."""
        base = reverse('lynx:active_oib_clients')
        for form_inst in formset.forms:
            field = form_inst.fields.get('client')
            if not field:
                continue
            # prefer bound value, fall back to initial model pk if present
            selected = ''
            try:
                val = form_inst['client'].value()
                if val:
                    selected = str(val)
                else:
                    init_val = form_inst.initial.get('client') if getattr(form_inst, 'initial', None) else None
                    if init_val:
                        selected = str(getattr(init_val, 'pk', init_val))
            except Exception:
                selected = ''
            name = f"{form_inst.prefix}-client"
            q = f"?name={quote(name)}"
            if selected:
                q += f"&selected={quote(selected)}"
            field.widget.attrs.update({
                'hx-get': base + q,
                # fetch options when the user first focuses the select; avoid repeated mousedown storms
                'hx-trigger': 'focus once',
                'hx-swap': 'innerHTML',
                'hx-target': 'this',
                # show a simple inline indicator while loading (optional)
                'hx-indicator': '.htmx-indicator',
            })

        # empty_form: use __prefix__ placeholder so client-side add works
        empty = formset.empty_form
        if empty and 'client' in empty.fields:
            name = f"{formset.prefix}-__prefix__-client"
            q = f"?name={quote(name)}"
            empty.fields['client'].widget.attrs.update({
                'hx-get': base + q,
                'hx-trigger': 'focus once',
                'hx-swap': 'innerHTML',
                'hx-target': 'this',
            })

    if request.method == 'POST':
        # pass user into form so it can honor admin override
        form = lfo.OIBServiceEventForm(request.POST, user=request.user)

        user_role_formset = OIBServiceEventUserRoleFormSet(request.POST, prefix=user_role_form_prefix)
        # Only show SIP instructors in the dropdown
        instructor_qs = dca.User.objects\
            .filter(groups__name='SIP', is_active=True)\
            .order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'))
        for fr in user_role_formset.forms:
            if 'instructor' in fr.fields:
                fr.fields['instructor'].queryset = instructor_qs

        client_formset = OIBServiceEventContactFormSet(request.POST, prefix=client_form_prefix)
        _attach_client_htmx_attrs(client_formset)

        if form.is_valid() and user_role_formset.is_valid() and client_formset.is_valid():
            # Either update existing or create new service event
            if edit_mode:
                service_event.oib_service_delivery_type = lm.OIBServiceDeliveryType.objects.get(
                    pk=form.cleaned_data['plan_type']
                )
                service_event.date = form.cleaned_data['note_date']
                service_event.length = parse_duration_string(form.cleaned_data['event_length'])
                service_event.note = form.cleaned_data['note']
                service_event.save()

                # Clean up related objects
                lm.OIBServiceEventInstructor.objects.filter(oib_service_event=service_event).delete()
                lm.OIBServiceEventContact.objects.filter(oib_service_event=service_event).delete()
                lm.OIBServiceEventOIBService.objects.filter(oib_service_event=service_event).delete()
            else:
                service_event = lm.OIBServiceEvent.objects.create(
                    oib_service_delivery_type=lm.OIBServiceDeliveryType.objects.get(pk=form.cleaned_data['plan_type']),
                    date=form.cleaned_data['note_date'],
                    length=parse_duration_string(form.cleaned_data['event_length']),
                    note=form.cleaned_data['note'],
                    entered_by=request.user,
                )

            # Create related objects for both add/edit modes
            for service in form.cleaned_data['services']:
                lm.OIBServiceEventOIBService.objects.create(
                    oib_service_event=service_event,
                    oib_service=service,
                )

            for row in user_role_formset.cleaned_data:
                if row and not row.get('DELETE', False):
                    lm.OIBServiceEventInstructor.objects.create(
                        oib_service_event=service_event,
                        instructor=row['instructor'],
                        oib_service_event_instructor_role=row['role'],
                    )

            for row in client_formset.cleaned_data:
                if row and not row.get('DELETE', False):
                    lm.OIBServiceEventContact.objects.create(
                        oib_service_event=service_event,
                        contact=row['client'],
                    )

            return redirect('lynx:oib_service_event_show', oib_service_event_id=service_event.id)
        else:
            # Form validation failed
            context = {
                'form': form,
                'formsets': {
                    'user_role_formset': user_role_formset,
                    'client_formset': client_formset,
                },
            }
            if edit_mode:
                context['service_event'] = service_event
                context['edit_mode'] = True
            return render(request, template_path, context)
    else:
        # GET request - show the form (pass user so template/widget knows admin availability)
        form = lfo.OIBServiceEventForm(initial=initial_data, user=request.user)
        user_role_formset = OIBServiceEventUserRoleFormSet(
            initial=user_role_initial,
            prefix=user_role_form_prefix
        )
        # Only show SIP instructors in the dropdown
        instructor_qs = dca.User.objects\
            .filter(groups__name='SIP', is_active=True)\
            .order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'))
        for fr in user_role_formset.forms:
            if 'instructor' in fr.fields:
                fr.fields['instructor'].queryset = instructor_qs

        client_formset = OIBServiceEventContactFormSet(
            initial=client_initial,
            prefix=client_form_prefix
        )
        _attach_client_htmx_attrs(client_formset)

        # minimize select rendering cost: keep only selected option(s) in each form's queryset
        for form_inst, init in zip(client_formset.forms, client_initial + [None] * max(0, len(client_formset.forms) - len(client_initial))):
            selected_id = None
            if init and init.get('client'):
                # initial provided as model instance in client_initial
                ci = init.get('client')
                selected_id = getattr(ci, 'pk', ci)
            # for safety: if POST or no selected, use empty queryset to avoid rendering thousands of options
            if selected_id:
                form_inst.fields['client'].queryset = lm.Contact.objects.filter(pk=selected_id)
            else:
                form_inst.fields['client'].queryset = lm.Contact.objects.none()
        # ensure the empty_form renders no full list
        client_formset.empty_form.fields['client'].queryset = lm.Contact.objects.none()

        context = {
            'form': form,
            'formsets': {
                'user_role_formset': user_role_formset,
                'client_formset': client_formset,
            },
        }
        if edit_mode:
            context['service_event'] = service_event
            context['edit_mode'] = True

        return render(request, template_path, context)

# "PLANS" (virtual)
# Outdated, but still useful for listing notes per program-agnostic plan
@login_required
def oib_plan_list_with_notes(request, contact_id):
    client = lm.Contact.objects.get(id=contact_id)

    # Get all distinct combinations of grant year and service delivery type
    plans = (
        lm.OIBServiceEvent.objects
        .filter(contacts__id=contact_id)
        .values(
            'id',
            'date',
            'oib_service_delivery_type__id',
            'oib_service_delivery_type__oib_service_delivery_type'
        )
        .annotate(
            grant_year=ddm.Case(
                ddm.When(date__month__gte=10, then=ddm.F('date__year')),
                default=ddm.F('date__year') - 1,
                output_field=ddm.IntegerField()
            )
        )
        .distinct()
        .order_by('-grant_year', 'oib_service_delivery_type__oib_service_delivery_type')
    )

    plans = list(plans)
    for plan in plans:
        plan['plan_group'] = f"10/1/{plan['grant_year']} - {plan['oib_service_delivery_type__oib_service_delivery_type']}"

    return render(request, "lynx/oib/oib_plan_list_with_notes.html", {
        "client": client,
        "plans": list(plans),
    })

def _get_plan_outcomes(contact_id, service_delivery_type_id, grant_year):
    """
    Returns: { OIBOutcomeType.id: OIBOutcomeChoice.id }
    """
    # preload all outcome types (IDs) so result always contains all keys
    outcome_types = lm.OIBOutcomeType.objects.all()
    outcome_type_ids = list(lm.OIBOutcomeType.objects.values_list('id', flat=True))

    # build defaults map from OIBOutcomeTypeChoice.default_choice == True
    defaults = {}
    default_choices_qs = (
        lm.OIBOutcomeTypeChoice.objects
        .filter(default_choice=True)
        .select_related('oib_outcome_choice')
    )
    for otc in default_choices_qs:
        ot_id = otc.oib_outcome_type_id
        choice_obj = otc.oib_outcome_choice
        defaults[ot_id] = choice_obj.id

    # start seeding with defaults (ensure all types present)
    otc_id_dict = {ot_id: defaults.get(ot_id, None) for ot_id in outcome_type_ids}

    # fetch existing outcomes (newest first per type via ordering)
    oib_outcome_qs = (
        lm.OIBOutcome.objects
        .filter(
            contact_id=contact_id,
            oib_service_delivery_type_id=service_delivery_type_id,
            grant_year=grant_year,
        )
        .select_related(
            'oib_outcome_type_choice',
            'oib_outcome_type_choice__oib_outcome_type',
            'oib_outcome_type_choice__oib_outcome_choice'
        )
        .order_by('oib_outcome_type_choice__oib_outcome_type_id', '-created')
    )

    seen = set()
    for outcome in oib_outcome_qs:
        type_id = outcome.oib_outcome_type_choice.oib_outcome_type_id
        if type_id in seen:
            continue  # already captured newest for this type
        choice_obj = outcome.oib_outcome_type_choice.oib_outcome_choice
        otc_id_dict[type_id] = choice_obj.id
        seen.add(type_id)

    outcome_choices_map = {o.id: o for o in lm.OIBOutcomeChoice.objects.all()}
    outcome_type_choice_tuples = []
    for ot in outcome_types:
        choice = outcome_choices_map.get(otc_id_dict.get(ot.id))
        outcome_type_choice_tuples.append(( ot.oib_outcome_type, choice ))

    return otc_id_dict, outcome_types, outcome_type_choice_tuples

@login_required
def oib_plan_list(request, contact_id):
    client = lm.Contact.objects.get(id=contact_id)
    plans = _get_plans(client)

    program_filter = (request.GET.get('program') or '').strip()

    if program_filter:
        plans = [plan for plan in plans if plan['program'] == program_filter]

    return render(request, "lynx/oib/oib_plan_list.html", {
        "client": client,
        "plans": plans,
        "program": request.GET.get('program')
    })

def _get_plans(client):
    service_events_qs = lm.OIBServiceEvent.for_client_with_grant_year(client.id)

    # Group events by the plan key (grant_year, service_delivery_type_id, program) preserving first-seen order.
    # Keep one OrderedDict mapping each key -> list[OIBServiceEvent].
    service_events_by_plan = OrderedDict()
    for service_event in service_events_qs:
        client_age_at_event = client.maybe_age_on(service_event.date)
        program = lm.Program.get_age_appropriate_oib_program(client_age_at_event)
        # normalize program to a simple code/string for the key (avoid model instances as dict keys)
        program = getattr(program, 'program', program) if program is not None else None
        key = (service_event.grant_year, service_event.oib_service_delivery_type_id, program)
        service_events_by_plan.setdefault(key, []).append(service_event)

    plans = []
    for (grant_year, service_delivery_type_id, program), service_events in service_events_by_plan.items():
        # use the first event as representative for names / labels
        first_service_event = service_events[0]
        maybe_sdt = first_service_event.oib_service_delivery_type
        service_delivery_type_name = maybe_sdt.oib_service_delivery_type if maybe_sdt.oib_service_delivery_type else ""
        plan_name = first_service_event.get_plan_name(grant_year, program, service_delivery_type_name)

        service_names = set().union(*(se.collect_service_names() for se in service_events))
        _otc_id_dict, _outcome_types, otc_tuples = _get_plan_outcomes(client.id, service_delivery_type_id, grant_year)

        # `service_events_by_plan` contains exactly what the name says, but don't want to
        # recreate that on each plan load, so added the concrete service event IDs to each
        # plan link to be read by the appropriate plan view.
        service_event_ids_for_plan = [se.id for se in service_events]
        plan_token = signing.dumps(service_event_ids_for_plan)

        plans.append({
            'id': plan_name,
            'grant_year': grant_year,
            'service_delivery_type_id': service_delivery_type_id,
            'service_delivery_type_name': service_delivery_type_name,
            'plan_name': plan_name,
            'program': program,
            'outcomes': otc_tuples,
            'service_names': sorted(service_names, key=str.lower),
            'plan_token': plan_token,
        })

    return plans

def _oib_plan_dict(request, contact_id, program, grant_year, service_delivery_type_id, edit_mode):
    token = request.GET.get('token')
    if token:
        try:
            event_ids = signing.loads(token)
        except signing.BadSignature:
            # invalid token — fallback to default behaviour or raise
            event_ids = None
    else:
        event_ids = None

    service_events = []
    if event_ids:
        # fetch only the events referenced by the token, preserve original order
        service_events = list(
            lm.OIBServiceEvent.objects
            .filter(id__in=event_ids)
            .select_related('oib_service_delivery_type')
            .prefetch_related('services', 'contacts')
            .order_by('-date')
        )
    else:
        # fallback: existing behaviour
        service_events = lm.OIBServiceEvent.in_grant_year(contact_id, service_delivery_type_id, grant_year)

    client = lm.Contact.objects.get(id=contact_id)
    service_delivery_type = lm.OIBServiceDeliveryType.objects.get(id=service_delivery_type_id)
    otc_id_dict, outcome_types, otc_tuples = _get_plan_outcomes(contact_id, service_delivery_type_id, grant_year)

    choices_by_type = {}
    if edit_mode:
        choices_by_type = {
            outcome_type.id: list(
                lm.OIBOutcomeTypeChoice.objects
                .filter(oib_outcome_type=outcome_type)
                .select_related('oib_outcome_choice')
                .order_by('oib_outcome_choice__oib_outcome_choice')
            )
            for outcome_type in outcome_types
        }

    return {
        "client": client,
        "grant_year": grant_year,
        "service_delivery_type": service_delivery_type,
        "service_delivery_type_id": service_delivery_type_id,
        "service_delivery_type_name": service_delivery_type.oib_service_delivery_type,
        "service_events": service_events,
        "outcome_types": outcome_types,
        "choices_by_type": choices_by_type,
        "program": program,
        "plan_name": service_events[0].get_plan_name(grant_year, program, service_delivery_type.oib_service_delivery_type),
        "plan_outcomes": otc_id_dict if edit_mode else otc_tuples,
        "edit_mode": edit_mode,
    }

# NOTE 2025_09_30_2124 There are 5 rolling outcomes / client / grant year / service delivery type,
#                      which are not re-set when a new grant year starts. (The client wouldn't
#                      magically loose their progress just because a new grant year started.)
@login_required
def oib_plan_show(request, contact_id, program, grant_year, service_delivery_type_id):
    opd = _oib_plan_dict( request, contact_id, program, grant_year, service_delivery_type_id, edit_mode=False )
    return render(request, "lynx/oib/oib_plan_show.html", opd)

@login_required
def oib_plan_edit(request, contact_id, program, grant_year, service_delivery_type_id):
    opd = _oib_plan_dict( request, contact_id, program, grant_year, service_delivery_type_id, edit_mode=True )

    if request.method == "POST":
        otc_id_dict = opd.get('plan_outcomes', {})      # in edit_mode this is the otc_id_dict
        outcome_types = opd.get('outcome_types', [])
        service_delivery_type = opd.get('service_delivery_type')

        for ot in outcome_types:
            otc_id_from_post = request.POST.get(f"outcome_{ot.id}")
            latest_otc_id = otc_id_dict.get(ot.id)
            if otc_id_from_post and str(otc_id_from_post) != str(latest_otc_id):
                otc = lm.OIBOutcomeTypeChoice.objects.get(
                    oib_outcome_type=ot,
                    oib_outcome_choice_id=otc_id_from_post
                )
                lm.OIBOutcome.objects.create(
                    contact_id=contact_id,
                    oib_outcome_type_choice=otc,
                    user=request.user,
                    oib_service_delivery_type=service_delivery_type,
                    grant_year=grant_year
                )
        return redirect('lynx:oib_plan_show', contact_id, program, grant_year, service_delivery_type_id)

    return render(request, "lynx/oib/oib_plan_show.html", opd)

# vim: set foldmethod=marker foldmarker={{-,}}- tabstop=4 shiftwidth=4 softtabstop=4 expandtab:
