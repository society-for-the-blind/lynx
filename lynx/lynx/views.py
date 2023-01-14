import csv
import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.db.models import Value as V
from django.db.models.functions import Concat, Replace, Lower
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView

from .filters import AssignmentFilter, ContactFilter
from .forms import IntakeNoteForm, LessonNoteForm, DocumentForm
from .models import (Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization,
                     ProgressReport, LessonNote, SipNote, Volunteer, SipPlan, ContactInfoView, Document, Vaccine,
                     Assignment)
from .support_functions import units_to_hours

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
def client_list_view(request):
    clients = Contact.objects.filter(active=1).order_by(Lower('last_name'), Lower('first_name'))
    return render(request, 'lynx/contact_list.html', {'clients': clients})


@login_required
def volunteer_list_view(request):
    volunteers = Contact.objects.filter(volunteer_check=1).order_by(Lower('last_name'), Lower('first_name'))
    return render(request, 'lynx/volunteer_list.html', {'volunteers': volunteers})


@login_required
def authorization_list_view(request, client_id):
    authorizations = Authorization.objects.filter(contact_id=client_id).order_by('-start_date')
    client = Contact.objects.get(id=client_id)
    return render(request, 'lynx/authorization_list.html', {'authorizations': authorizations, 'client': client})


@login_required
def sipplan_list_view(request, client_id):
    plans = SipPlan.objects.filter(contact_id=client_id).order_by('-plan_date')
    client = Contact.objects.get(id=client_id)
    return render(request, 'lynx/sipplan_list.html', {'plans': plans, 'client': client})


@login_required
def sipnote_list_view(request, client_id):
    notes = SipNote.objects.filter(contact_id=client_id).order_by('-note_date')
    client = Contact.objects.get(id=client_id)
    return render(request, 'lynx/sipnote_list.html', {'notes': notes, 'client': client})


@login_required
def instructor_list_view(request):
    query = request.GET.get('q')
    instructors = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
    if query:
        instructor_list = User.objects.filter(groups__name='SIP').order_by(Lower('last_name'))
        object_list = Contact.objects.filter(
            Q(full_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        object_list = object_list.order_by(Lower('last_name'), Lower('first_name'))
    else:
        object_list = None
    return render(request, 'lynx/instructor_search.html', {'instructors': instructors})


@login_required
def client_result_view(request):
    query = request.GET.get('q')
    clients = Contact.objects.filter(active=1).order_by(Lower('last_name'), Lower('first_name'))
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
    return render(request, 'lynx/client_search.html', {'object_list': object_list, 'clients': clients})


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
            year=request.GET.get('selYear')).order_by(Lower('authorization__contact__last_name'),
                                                      'authorization__intake_service_area__agency')

    else:
        object_list = None
        given_month = None
    return render(request, 'lynx/monthly_progress_reports.html', {'object_list': object_list, 'givenMonth': given_month,
                                                                  'givenYear': request.GET.get('selYear')})


@login_required
def assignment_detail(request, contact_id):
    instructor_list = Assignment.objects.filter(contact_id=contact_id).order_by('-assignment_date')
    contact = Contact.objects.filter(pk=contact_id)
    return render(request, 'lynx/assignment_detail.html',
                  {'instructor_list': instructor_list, "contact_id": contact_id, 'contact': contact})


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
        context['sip_list'] = SipNote.objects.filter(contact_id=self.kwargs['pk']).order_by(
            F('note_date').desc(nulls_last=True))
        context['sip_plan_list'] = SipPlan.objects.filter(contact_id=self.kwargs['pk']).order_by('-plan_date')
        context['emergency_list'] = EmergencyContact.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['document_list'] = Document.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['vaccine_list'] = Vaccine.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
        context['instructor_list'] = Assignment.objects.filter(contact_id=self.kwargs['pk']).order_by('-created')
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
                      '7': '-07-31', '8': '-08-31', '9': '-09-30', '10': '-10-31', '11': '-11-30', '12': '-12-31'}

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
            if note['billed_units']:
                units = float(note['billed_units'])
                all_units += units
                class_count += 1

        total_hours = units_to_hours(all_units)
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
        notes = LessonNote.objects.filter(authorization_id=auth_id).filter(date__month=month).filter(
            date__year=year).order_by(
            'date').values()
        reports = ProgressReport.objects.filter(authorization_id=auth_id).values()
        month_report = ProgressReport.objects.filter(authorization_id=auth_id).filter(month=month).filter(
            year=year).values()[:1]
        context['month_report'] = month_report
        authorization = Authorization.objects.filter(id=auth_id).values()

        context['note_list'] = notes

        contact_id = authorization[0]['outside_agency_id']
        outside = Contact.objects.filter(id=contact_id).values()
        context['payment'] = outside[0]['first_name'] + ' ' + outside[0]['last_name'] + ' - ' + outside[0]['company']
        # contact_id = outside[0]['contact_id']
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


class InstructorDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'lynx/instructor_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(InstructorDetailView, self).get_context_data(**kwargs)
        context['assignment_list'] = Assignment.objects.filter(instructor_id=self.kwargs['pk']).order_by(
            '-assignment_date')
        return context


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
                    client_condensed[client.id]['full_phone'] = client_condensed[client.id][
                                                                    'full_phone'] + ', ' + client.full_phone
                if client_condensed[client.id]['email'] != client.email and client.email is not None:
                    client_condensed[client.id]['email'] = client_condensed[client.id]['email'] + ', ' + client.email
                if client_condensed[client.id]['zip_code'] != client.zip_code and client.zip_code is not None:
                    client_condensed[client.id]['zip_code'] = client_condensed[client.id][
                                                                  'zip_code'] + ', ' + client.zip_code
                if client_condensed[client.id]['county'] != client.county and client.county is not None:
                    client_condensed[client.id]['county'] = client_condensed[client.id]['county'] + ', ' + client.county
                if client_condensed[client.id]['bad_address'] != client.bad_address and client.bad_address is not None:
                    client_condensed[client.id]['bad_address'] = client_condensed[client.id][
                                                                     'bad_address'] + ', ' + str(client.bad_address)
                if (client_condensed[client.id]['do_not_contact'] != client.do_not_contact
                        and client.do_not_contact is not None):
                    client_condensed[client.id]['do_not_contact'] = client_condensed[client.id][
                                                                        'do_not_contact'] + ', ' + str(
                        client.do_not_contact)
                if (client_condensed[client.id]['remove_mailing'] != client.remove_mailing
                        and client.remove_mailing is not None):
                    client_condensed[client.id]['remove_mailing'] = (client_condensed[client.id]['remove_mailing']
                                                                     + ', ' + str(client.remove_mailing))
            else:
                client_condensed[client.id] = {}
                client_condensed[client.id]['full_phone'] = client.full_phone if client.full_phone is not None else ''
                client_condensed[client.id]['full_name'] = client.full_name if client.full_name is not None else ''
                client_condensed[client.id]['first_name'] = client.first_name if client.first_name is not None else ''
                client_condensed[client.id]['last_name'] = client.last_name if client.last_name is not None else ''
                client_condensed[client.id]['email'] = client.email if client.email is not None else ''
                client_condensed[client.id][
                    'intake_date'] = client.intake_date if client.intake_date is not None else ''
                client_condensed[client.id]['zip_code'] = client.zip_code if client.zip_code is not None else ''
                client_condensed[client.id]['county'] = client.county if client.county is not None else ''
                client_condensed[client.id]['age_group'] = client.age_group if client.age_group is not None else ''
                client_condensed[client.id][
                    'address_one'] = client.address_one if client.address_one is not None else ''
                client_condensed[client.id][
                    'address_two'] = client.address_two if client.address_two is not None else ''
                client_condensed[client.id]['suite'] = client.suite if client.suite is not None else ''
                client_condensed[client.id]['city'] = client.city if client.city is not None else ''
                client_condensed[client.id]['state'] = client.state if client.state is not None else ''
                client_condensed[client.id]['region'] = client.region if client.region is not None else ''
                client_condensed[client.id]['bad_address'] = str(
                    client.bad_address) if client.bad_address is not None else ''
                client_condensed[client.id]['do_not_contact'] = str(
                    client.do_not_contact) if client.do_not_contact is not None else ''
                client_condensed[client.id]['deceased'] = str(client.deceased) if client.deceased is not None else ''
                client_condensed[client.id]['remove_mailing'] = str(
                    client.remove_mailing) if client.remove_mailing is not None else ''
                client_condensed[client.id]['active'] = str(client.active) if client.active is not None else ''
                client_condensed[client.id]['sip_client'] = str(
                    client.sip_client) if client.sip_client is not None else ''
                client_condensed[client.id]['core_client'] = str(
                    client.core_client) if client.core_client is not None else ''

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


class ManualView(LoginRequiredMixin, TemplateView):
    template_name = 'lynx/manual.html'


@login_required
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


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
def assignment_advanced_result_view(request):
    if request.method == 'GET':
        strict = True
        f = AssignmentFilter(request.GET, queryset=Assignment.objects.all().order_by('-assignment_date'))
        assignment_condensed = {}
        for assignment in f.qs:
            assignment_condensed[assignment.id] = {}
            assignment_condensed[assignment.id]['assignment_date'] = (
                assignment.assignment_date if assignment.assignment_date is not None else '')
            assignment_condensed[assignment.id]['client_id'] = (
                assignment.contact_id if assignment.contact_id is not None else '')
            assignment_condensed[assignment.id]['client_first_name'] = (
                assignment.contact.first_name if assignment.contact.first_name is not None else '')
            assignment_condensed[assignment.id]['client_last_name'] = (
                assignment.contact.last_name if assignment.contact.last_name is not None else '')
            assignment_condensed[assignment.id]['note'] = assignment.note if assignment.note is not None else ''
            assignment_condensed[assignment.id]['assigned_by_first_name'] = (
                assignment.user.first_name if assignment.user.first_name is not None else '')
            assignment_condensed[assignment.id]['assigned_by_last_name'] = (
                assignment.user.last_name if assignment.user.last_name is not None else '')
            assignment_condensed[assignment.id]['assignment_status'] = (
                assignment.assignment_status if assignment.assignment_status is not None else '')
            assignment_condensed[assignment.id]['instructor_first_name'] = (
                assignment.instructor.first_name if assignment.instructor.first_name is not None else '')
            assignment_condensed[assignment.id]['instructor_last_name'] = (
                assignment.instructor.last_name if assignment.instructor.last_name is not None else '')

    else:
        f = AssignmentFilter()
        assignment_condensed = {}

    return render(request, 'lynx/instructor_search.html', {'filter': f, 'assignment_list': assignment_condensed})

#
# @login_required
# def change_assignment_status(request, assignment_id, status):
#     if status == 'Assigned':
#         new_status = 'In Progress'
#     elif status == 'InProgress':
#         new_status = 'Completed'
#     else:
#         new_status = 'Completed'
#
#     assignment = Assignment.objects.get(id=assignment_id)
#     assignment.status = new_status
#     assignment.save()
#
#     # f = AssignmentFilter()
#     # assignment_condensed = {}
#     return redirect('lynx/instructors/')
#     # return render(request, 'lynx/instructor_search.html', {'filter': f, 'assignment_list': assignment_condensed})
