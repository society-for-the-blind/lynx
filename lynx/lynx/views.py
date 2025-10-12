from collections import defaultdict
from datetime    import datetime, date, timedelta
from urllib.parse import quote
from django      import forms
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins     import LoginRequiredMixin  \
                                         , UserPassesTestMixin

from django.contrib import messages
from django.contrib.auth import models as dca

from django.core.mail      import send_mail
from django.core.paginator import Paginator

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


# TODO RESTify  `urls.py` to  get  rid  of the  `path_part`
#      duplication in the views below
#
# E.g., `sipplans` and `sip1854plans` should simply be
# `plans` with  and added program identifier  as input
# before/after the client  id. Does Django's `urls.py`
# allow specifying parameters to be passed to views?

def parse_path_for_program(request):
    # (Pdb) request.path
    # '/lynx/...sip1854...../11469'
    # (Pdb) request.path.split('/')
    # ['', 'lynx', '...sip1854.....', '11469']
    path_part = request.path.split('/')[2]
    # program_path_part = path_part[:-5]
    program_path_part = re.search('(?P<program>sip(\d{4})?)', path_part).group('program')

    if   program_path_part == 'sip':

        program_name    = 'SIP'
        plan_model      = lm.SipPlan
        plan_form_model = lfo.SipPlanForm
        note_model      = lm.SipNote
        note_form       = lfo.SipNoteForm

    elif program_path_part == 'sip1854':

        program_name    = '18-54'
        plan_model      = lm.Sip1854Plan
        plan_form_model = lfo.Sip1854PlanForm
        note_model      = lm.Sip1854Note
        note_form       = lfo.Sip1854NoteForm

    else:
        raise ValueError(f"Only `sip` and `sip1854` prefixes are supported. \
                           Got: '{ program_path_part }'.")

    return { 'program_name':      program_name      \
           , 'program_path_part': program_path_part \
           , 'plan_model':        plan_model        \
           , 'plan_form_model':   plan_form_model   \
           , 'note_model':        note_model        \
           , 'note_form':         note_form         \
           }

@login_required
def plan_list_view(request, client_id):
    # import pdb; pdb.set_trace()
    client = lm.Contact.objects.get(id=client_id)

    p = parse_path_for_program( request )
    plans = p['plan_model']               \
            .objects                      \
            .filter(contact_id=client_id) \
            .annotate( date_substring=ddmf.Cast( ddmf.Substr( 'plan_name'                      \
                                                  , 1                                          \
                                                  , ddmf.StrIndex('plan_name', ddm.Value(' ')) \
                                                  )
                                          , ddm.DateField() \
                                          )                 \
                     )                                      \
            .order_by('-date_substring')

    return render( request                                       \
                 , 'lynx/plan_list.html'                         \
                 , { 'plans':             plans                  \
                   , 'client':            client                 \
                   , 'program_name':      p['program_name']      \
                   , 'program_path_part': p['program_path_part'] \
                   }                                             \
                 )


@login_required
def plan_note_list_view(request, client_id):
    # notes = lm.SipNote.objects.filter(contact_id=client_id).order_by('-note_date')
    client = lm.Contact.objects.get(id=client_id)

    p = parse_path_for_program( request )
    notes = p['note_model']               \
            .objects                      \
            .filter(contact_id=client_id) \
            .select_related('sip_plan')   \
            .order_by('-note_date')

    return render( request
                 , 'lynx/plan_note_list.html'
                 , { 'notes': notes
                   , 'client': client
                   , 'program_name':      p['program_name']      \
                   , 'program_path_part': p['program_path_part'] \
                   }
                 )

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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
    return render(request, 'lynx/intake/intake_form.html', {'form': form})


@login_required
def add_plan_note(request, contact_id):
    contact = {'contact_id': contact_id}
    client = lm.Contact.objects.get(id=contact_id)
    plan_id = request.GET.get('plan_id')
    # import pdb; pdb.set_trace()

    p = parse_path_for_program( request )
    form_class = p['note_form']

    if plan_id:
        form = form_class(initial={'plan': plan_id}, **contact, plan_id=plan_id)
    else:
        form = form_class(**contact)

    # form = form_class(request, contact_id=contact_id)
    if request.method == 'POST':

        # NOTE deactivate creating new plan with a new note (it will confuse users)
        #      See also forms.py if re-activation needed. {{-

        # if request.POST['sip_plan'].isnumeric():
        #     post = request.POST
        # else:
        #     post_with_new_plan = request.POST.copy()
        #     post_with_new_plan['plan_type'] = post_with_new_plan['sip_plan']
        #     post_with_new_plan['plan_date_month'] = post_with_new_plan['note_date_month']
        #     post_with_new_plan['plan_date_day'] = post_with_new_plan['note_date_day']
        #     post_with_new_plan['plan_date_year'] = post_with_new_plan['note_date_year']
        #     post_with_new_plan['note'] = ''
        #     if 'at_devices' in post_with_new_plan:
        #         post_with_new_plan['at_services'] = post_with_new_plan['at_devices']
        #     if 'support' in post_with_new_plan:
        #         post_with_new_plan['support_services'] = post_with_new_plan['support']
        #     if 'services' in post_with_new_plan:
        #         post_with_new_plan['other_services']   = post_with_new_plan['services']
        #     plan_form = lfo.SipPlanForm(post_with_new_plan)
        #     # Not sure what happens if this fails, but then this should never fail.
        #     if plan_form.is_valid():
        #         # import pdb; pdb.set_trace()
        #         new_plan_id = save_plan(plan_form, request.user, post_with_new_plan, contact_id)
        #         post_with_new_plan['sip_plan'] = str(new_plan_id)
        #         post_with_new_plan['note'] = request.POST['note']
        #         post = post_with_new_plan
        # }}-

        post = request.POST
        form = form_class(post, contact_id=contact_id)

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

        next_url = request.GET.get('next', '')  # Fallback to an empty string if 'next' is not present
        # import pdb; pdb.set_trace()
        if next_url:
            # Optional: Validate next_url before redirecting
            return HttpResponseRedirect(next_url)
        else:
            # If 'next' parameter isn't provided, redirect to a default location
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))

    return render( request                              \
                 , 'lynx/add_plan_note.html'            \
                 , { 'form':          form              \
                   , 'contact_id':    contact_id        \
                   , 'client':        client            \
                   , 'program_name':  p['program_name'] \
                   }                                    \
                 )


def save_plan(form, request_user, request_post, contact_id):
    form = form.save(commit=False)
    form.instructor = request_user.first_name + request_user.last_name
    form.plan_name =   request_post.get('plan_date_month') \
                     + '/'                                 \
                     + request_post.get('plan_date_day')   \
                     + '/'                                 \
                     + request_post.get('plan_date_year')  \
                   + ' - '                                 \
                   + request_post.get('plan_type')         \
                   + ' - '                                 \
                   + form.instructor
    # form.plan_date = request.POST.get('start_date')
    form.contact_id = contact_id
    form.user_id = request_user.id
    form.save()
    return form.pk

@login_required
def add_plan(request, contact_id):
    p = parse_path_for_program( request )
    # import pdb; pdb.set_trace()
    form = p['plan_form_model']()

    if request.method == 'POST':
        form = p['plan_form_model'](request.POST)

        if form.is_valid():
            new_plan_id = save_plan(form, request.user, request.POST, contact_id)
            return HttpResponseRedirect( reverse( f"lynx:{ p['program_path_part'] }_plan_detail" \
                                                , kwargs={'pk': new_plan_id}                     \
                                                )                                                \
                                       )

    return render( request                                       \
                 , 'lynx/add_plan.html'                          \
                 , { 'form': form                                \
                   , 'program_name':      p['program_name']      \
                   , 'program_path_part': p['program_path_part'] \
                   }                                             \
                 )


@login_required
def add_assignments(request, contact_id):
    form = lfo.AssignmentForm()
    # import pdb; pdb.set_trace()
    instructors = dca.User.objects.filter(groups__name='SIP').order_by(ddmf.Lower('last_name'))
    program_options = ["SIP", "1854"]
    assignment_priorities = ["New", "Returning"]

    if request.method == 'POST':
        form = lfo.AssignmentForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.contact_id = contact_id
            form.user_id = request.user.id
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

            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client_show', args=(contact_id,)))
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


@login_required
def assignment_detail(request, contact_id):
    instructor_list = lm.Assignment.objects.filter(contact_id=contact_id).order_by('-assignment_date')
    # contact = lm.Contact.objects.get(id=contact_id).first()
    contact = lm.Contact.objects.filter(pk=contact_id).first()
    # import pdb; pdb.set_trace()
    return render(request, 'lynx/assignment_detail.html', {'instructor_list': instructor_list, "contact_id": contact_id, 'contact': contact})

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


class PlanDetailView(LoginRequiredMixin, DetailView):
    template_name = 'lynx/plan_detail.html'

    def get_queryset(self):
        p = parse_path_for_program( self.request )
        self.model = p['plan_model']
        self.queryset = p['plan_model'].objects.all()
        return super(PlanDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        p = parse_path_for_program( self.request )
        # import pdb; pdb.set_trace()
        context = super(PlanDetailView, self).get_context_data(**kwargs)
        context['plan_note_list'] = p['note_model'].objects.filter(sip_plan_id=self.kwargs['pk']).order_by('-note_date')
        context['program_name'] = p['program_name']
        context['program_path_part'] = p['program_path_part']
        return context

@login_required
def historical_sip_plans(request, client_id):
    """
    Show links to historical SIP/SIP1854 plans and notes for a client
    only if records exist.
    """
    client = get_object_or_404(lm.Contact, pk=client_id)

    counts = {
        'sip_plans':     lm.SipPlan.objects.filter(contact_id=client_id).count(),
        'sip1854_plans': lm.Sip1854Plan.objects.filter(contact_id=client_id).count(),
        'sip_notes':     lm.SipNote.objects.filter(contact_id=client_id).count(),
        'sip1854_notes': lm.Sip1854Note.objects.filter(contact_id=client_id).count(),
    }

    return render(request,
                  'lynx/historical_sip_plans.html',
                  {'client': client, 'counts': counts})

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

        # add historical SIP / 18-54 existence flag and counts
        client_id = self.kwargs['pk']
        sip_exists = lm.SipPlan.objects.filter(contact_id=client_id).exists()
        sip1854_exists = lm.Sip1854Plan.objects.filter(contact_id=client_id).exists()
        sip_note_exists = lm.SipNote.objects.filter(contact_id=client_id).exists()
        sip1854_note_exists = lm.Sip1854Note.objects.filter(contact_id=client_id).exists()
        context['has_historical_sip_plans'] = any([sip_exists, sip1854_exists, sip_note_exists, sip1854_note_exists])
        context['historical_sip_counts'] = {
            'sip_plans':     lm.SipPlan.objects.filter(contact_id=client_id).count(),
            'sip1854_plans': lm.Sip1854Plan.objects.filter(contact_id=client_id).count(),
            'sip_notes':     lm.SipNote.objects.filter(contact_id=client_id).count(),
            'sip1854_notes': lm.Sip1854Note.objects.filter(contact_id=client_id).count(),
        }

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

        return HttpResponseRedirect(reverse('lynx:client_show', args=(self.object.pk,)))

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
            return redirect('lynx:client_show', pk=intake.contact_id)

        if action == 'confirm':
            new_birth_date = date.fromisoformat(pending['new_birth_date'])
            violating_program_codes = {v['program'] for v in pending['violations']}
            today = date.today()
            memberships = (
                intake.contact.contactprogram_set
                .filter(end_date__isnull=True, program__program__in=violating_program_codes)
                .select_related('program')
            )
            for m in memberships:
                m.end_date = today
                m.save()

            intake.birth_date = new_birth_date
            intake.save()

            request.session.pop(session_key, None)
            return redirect('lynx:client_show', pk=intake.contact_id)

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


class PlanNoteUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['note', 'note_date', 'at_devices',  'independent_living', 'orientation', 'communications', 'dls',
              'support', 'advocacy', 'counseling', 'information', 'services', 'retreat', 'in_home', 'seminar',
              'modesto', 'group', 'community', 'class_hours', 'sip_plan', 'instructor']
    template_name = 'lynx/plan_note_edit.html'

    def get_queryset(self):
        p = parse_path_for_program( self.request )
        self.model = p['note_model']
        self.queryset = p['note_model'].objects.all()
        return super(PlanNoteUpdateView, self).get_queryset()

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        # NOTE Don't check for `next_url`, because it should always
        #      be there as deleting a note would always happen in a
        #      context.
        return next_url

    def get_context_data(self, **kwargs):
        p = parse_path_for_program( self.request )
        context = super(PlanNoteUpdateView, self).get_context_data(**kwargs)
        context['program_name'] = p['program_name']
        return context

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
        # action = "/lynx/sipnotes/" + str(post.contact_id)
        # return HttpResponseRedirect(action)
        return super().form_valid(form)

    def get_form(self, form_class=None):
        p = parse_path_for_program( self.request )

        form = super().get_form(form_class=form_class)
        form.fields['note_date'].widget = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields['note_date'].required = True
        form.fields['at_devices'].label = "Assistive Technology Devices and Services"
        form.fields['independent_living'].label = "Independent Living and Adjustment Services"
        form.fields['orientation'].label = "Orientation & Mobility Training"
        form.fields['communications'].label = "Communication Skills Training"
        form.fields['dls'].label = "Daily Living Skills Training"
        form.fields['advocacy'].label = "Advocacy Training"
        form.fields['information'].label = "Information and Referral"
        form.fields['counseling'].label = "Adjustment Counseling"
        form.fields['support'].label = "Supportive Services"
        form.fields['services'].label = "Other IL/A Services"

        class_hours_choices = [
            ('', '---------'),
                                ('0.25', '15 minutes'),         ('0.5', '30 minutes'),         ('0.75', '45 minutes'),
            ('1.0', '1 hour'),  ('1.25', '1 hour 15 minutes'),  ('1.5', '1 hour 30 minutes'),  ('1.75', '1 hour 45 minutes'),
            ('2.0', '2 hours'), ('2.25', '2 hours 15 minutes'), ('2.5', '2 hours 30 minutes'), ('2.75', '2 hours 45 minutes'),
            ('3.0', '3 hours'), ('3.25', '3 hours 15 minutes'), ('3.5', '3 hours 30 minutes'), ('3.75', '3 hours 45 minutes'),
            ('4.0', '4 hours'), ('4.25', '4 hours 15 minutes'), ('4.5', '4 hours 30 minutes'), ('4.75', '4 hours 45 minutes'),
            ('5.0', '5 hours'), ('5.25', '5 hours 15 minutes'), ('5.5', '5 hours 30 minutes'), ('5.75', '5 hours 45 minutes'),
            ('6.0', '6 hours'), ('6.25', '6 hours 15 minutes'), ('6.5', '6 hours 30 minutes'), ('6.75', '6 hours 45 minutes'),
            ('7.0', '7 hours'), ('7.25', '7 hours 15 minutes'), ('7.5', '7 hours 30 minutes'), ('7.75', '7 hours 45 minutes'),
            ('8.0', '8 hours')
        ]

        # Update the class_hours field with the new choices
        form.fields['class_hours'].choices = class_hours_choices
        form.fields['class_hours'].required = True

        form.fields['sip_plan'].label = f"{ p['program_name'] } plan"
        form.fields['sip_plan'].required = True
        # import pdb; pdb.set_trace()
        return form


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['note', 'at_services', 'independent_living', 'orientation', 'communications', 'dls', 'advocacy',
              'counseling', 'information', 'other_services', 'plan_name', 'living_plan_progress', 'at_outcomes',
              'employment_outcomes', 'community_plan_progress', 'ila_outcomes', 'support_services', 'plan_date']
    template_name = 'lynx/plan_edit.html'

    def get_queryset(self):
        p = parse_path_for_program( self.request )
        self.model = p['plan_model']
        self.queryset = p['plan_model'].objects.all()
        return super(PlanUpdateView, self).get_queryset()

    def get_success_url(self):
        p = parse_path_for_program( self.request )
        next_url = self.request.GET.get('next')
        # import pdb; pdb.set_trace()
        if next_url:
            return next_url
        else:
            # NOTE Returns to the detailed view of the plan being edited
            return reverse(f"lynx:{ p['program_path_part'] }_plan_detail", kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        p = parse_path_for_program( self.request )
        context = super(PlanUpdateView, self).get_context_data(**kwargs)
        context['program_name'] = p['program_name']
        context['program_path_part'] = p['program_path_part']
        return context

    def get_form(self, form_class=None):
        p = parse_path_for_program( self.request )
        notes = p['note_model'].objects.filter(sip_plan_id=self.kwargs['pk'])

        form = super().get_form(form_class=form_class)
        form.fields['plan_date'].widget              = forms.SelectDateWidget(years=list(range(1900, 2100)))
        form.fields['at_services'].label             = "Assistive Technology Devices and Services"
        form.fields['independent_living'].label      = "Independent Living and Adjustment Services"
        form.fields['orientation'].label             = "Orientation & Mobility Training"
        form.fields['communications'].label          = "Communication Skills Training"
        form.fields['dls'].label                     = "Daily Living Skills Training"
        form.fields['plan_date'].label               = "Start Date"
        form.fields['advocacy'].label                = "Advocacy Training"
        form.fields['information'].label             = "Information and Referral"
        form.fields['counseling'].label              = "Adjustment Counseling"
        form.fields['support_services'].label        = "Supportive Services"
        form.fields['other_services'].label          = "Other IL/A Services"
        form.fields['living_plan_progress'].label    = "Living Situation Outcomes"
        form.fields['community_plan_progress'].label = "Home and Community involvement Outcomes"
        form.fields['at_outcomes'].label             = "AT Goal Outcomes"
        form.fields['ila_outcomes'].label            = "IL/A Service Goal Outcomes"

        is_me = self.request.user.username == 'agulyas'
        form.fields['plan_name'].disabled = False if is_me else True

        # NOTE (soft deletion) {{-
        #      This section enables or disables setting certain OIB
        #      outcomes when  editing a  plan depending  on whether
        #      the  plan has  notes  that have  the right  services
        #      checked.  Now  that  outcomes  can be  set  on  plan
        #      creation,  it  doesn't  make sense  to  impose  such
        #      restrictions.
        # }}-
        # TODO Re-evaluate if  outcome setting  is disabled {{-
        #      again on plan creation.
        """
        ils = True
        ats = True
        outcomes = True
        for note in notes:
            if     note.orientation    \
                or note.communications \
                or note.dls            \
                or note.advocacy       \
                or note.counseling     \
                or note.information    \
                or note.services       \
                or note.support:

                ils = False

            if note.at_devices or note.at_services:
                 ats = False

        if not ils or not ats:
            outcomes = False

        form.fields['at_outcomes'].disabled = ats
        form.fields['ila_outcomes'].disabled = ils
        # Need to ask DOR
        form.fields['living_plan_progress'].disabled = outcomes
        form.fields['community_plan_progress'].disabled = outcomes
        form.fields['employment_outcomes'].disabled = outcomes
        """
        # }}-

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


class PlanDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'lynx/plan_confirm_delete.html'

    def get_queryset(self):
        p = parse_path_for_program( self.request )
        self.model = p['plan_model']
        self.queryset = p['plan_model'].objects.all()
        return super(PlanDeleteView, self).get_queryset()

    def get_success_url(self):
        p = parse_path_for_program( self.request )
        client_id = self.kwargs['client_id']
        return reverse_lazy(f"lynx:{ p['program_path_part'] }_plan_list", kwargs={'client_id': client_id})


class PlanNoteDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'lynx/plan_note_confirm_delete.html'

    def get_queryset(self):
        p = parse_path_for_program( self.request )
        self.model = p['note_model']
        self.queryset = p['note_model'].objects.all()
        return super(PlanNoteDeleteView, self).get_queryset()

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        # NOTE Don't check for `next_url`, because it should always
        #      be there as deleting a note would always happen in a
        #      context.
        return next_url


class IntakeNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.IntakeNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client_show', kwargs={'pk': client_id})


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
        return reverse_lazy('lynx:client_show', kwargs={'pk': client_id})


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
        return reverse_lazy('lynx:client_show', kwargs={'pk': client_id})


class VaccineDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Vaccine

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client_show', kwargs={'pk': client_id})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Document

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client_show', kwargs={'pk': client_id})


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
def contact_filter(request):
    if request.method == 'GET':
        excel = request.GET.get('excel', False)
        # Use Contact model instead of ContactInfoView
        f = lfi.ContactFilter(request.GET, queryset=lm.ContactInfoView.objects.all().order_by('last_name'))

        client_condensed = {}
        for client in f.qs:
            client_condensed[client.id] = {
                'full_name': f"{client.last_name}, {client.first_name}",
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email_set.first().email if client.email_set.exists() else '',
                'phone': client.phone_set.first().phone if client.phone_set.exists() else '',
                'intake_date': getattr(client, 'intake_date', ''),
                'age_group': getattr(client, 'age_group', ''),
                'zip_code': client.address_set.first().zip_code if client.address_set.exists() else '',
                'county': client.address_set.first().county if client.address_set.exists() else '',
                'address_one': client.address_set.first().address_one if client.address_set.exists() else '',
                'address_two': client.address_set.first().address_two if client.address_set.exists() else '',
                'suite': client.address_set.first().suite if client.address_set.exists() else '',
                'city': client.address_set.first().city if client.address_set.exists() else '',
                'state': client.address_set.first().state if client.address_set.exists() else '',
                'region': client.address_set.first().region if client.address_set.exists() else '',
                'bad_address': str(client.address_set.first().bad_address) if client.address_set.exists() else '',
                'do_not_contact': str(client.do_not_contact),
                'deceased': str(client.deceased),
                'remove_mailing': str(client.remove_mailing),
                'active': str(client.active),
                # Programs as comma-separated string
                'programs': ", ".join([p.program for p in client.programs.all()]),
            }

        if excel == 'true':
            filename = "Lynx Search Results"
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

            writer = csv.writer(response)
            writer.writerow([
                "Full Name", "First Name", "Last Name", "Intake Date", "Age Group", "County", "Email", "Phone",
                "Address 1", "Address 2", "Suite", "City", "State", "Zip Code", "Region", "Bad Address",
                "Do Not Contact", "Deceased", "Remove Mailing", "Active", "Programs"
            ])
            for client in client_condensed.values():
                writer.writerow([
                    client['full_name'], client['first_name'], client['last_name'], client['intake_date'],
                    client['age_group'], client['county'], client['email'], client['phone'],
                    client['address_one'], client['address_two'], client['suite'], client['city'], client['state'],
                    client['zip_code'], client['region'], client['bad_address'], client['do_not_contact'],
                    client['deceased'], client['remove_mailing'], client['active'], client['programs']
                ])
            return response

    else:
        f = lfi.ContactFilter()
        client_condensed = {}
    return render(request, 'lynx/contact/contact_filter.html', {'filter': f, 'client_list': client_condensed})

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


def is_assessed(ila_outcomes, at_outcomes):
    ila_assessed = False
    at_assessed = False
    if ila_outcomes and ila_outcomes != "Not assessed":
        ila_assessed = True
    if at_outcomes and at_outcomes != "Not assessed":
        at_assessed = True
    if at_assessed and ila_assessed:
        return "Assessed"
    else:
        return "Not Assessed"


def get_current_date_minus_one_year():
    now = datetime.now()
    return date(now.year -1, now.month, now.day)

# DEPRECATION NOTE
# The original idea was  that the default "Assignments
# after date"  will always  be the current  grant year
# start date,  but then  this turned out  to be  a bad
# idea  as  assignments  don't simply  vanish  when  a
# new  grant year  starts.  Still, the  list needs  to
# be  limited,  so  a  compromise  was  made  to  show
# assignments 1 year back.

def get_current_grant_year_startdate():
    now = datetime.now()
    grant_year_start = date(now.year, 10, 1)

    if grant_year_start < now.date():
        return grant_year_start
    else:
        return date(now.year - 1, 10, 1)


# TODO Replace `sip1845` prefixes with `ab2480`
#          AND
#      Change `sip_plan_id` foreign key in `lynx_sip1854note` table
#      (plus also the table names with that prefix...)
#
#      `lynx_sipnote`  and `lynx_sip1845note`  both have  a
#      foreign key  called `sip_plan_id`  but it  should be
#      `ab2480_plan_id`  to make  relationships  in the  DB
#      unambiguous (even if it is more work in the app).
#
#     NOTE Why `ab2480_plan_id` and not `sip1854_plan_id`?
#
#          Because the `sip1854` prefix  has been a mistake all
#          along.  The "18-54"  program is  an unofficial  name
#          using a mnemonic to make  it easier to remember that
#          clients in the  AB2480 have to be between  18 and 54
#          years  of age.  (It doesn't  help that  even in  the
#          official forms it is sometimes referred to as "Under
#          55 7-OB" or simply just as "7-OB" program...)
@login_required
def assignment_advanced_result_view(request):
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
            # initial_data = {'assignment_date_lt': timezone.now()}
            # f = lfi.AssignmentFilter(request.GET, queryset=lm.Assignment.objects.all())
            # f = lfi.AssignmentFilter(request.GET or initial_data, queryset=lm.Assignment.objects.all().order_by('-assignment_date'))
            f = lfi.AssignmentFilter(request.GET, queryset=lm.Assignment.objects.all().order_by('-assignment_date'))
            # notes = lm.SipNote.objects.all()
        else:
            initial_data = {
                'assignment_date_gt': get_current_date_minus_one_year()
            ,   'instructor': request.user.id
            }
            f = lfi.AssignmentFilter(initial_data, queryset=lm.Assignment.objects.all().order_by('-assignment_date'))

        assignment_condensed = {}
        for assignment in f.qs:
            assignment_condensed[assignment.id] = {}
            assignment_condensed[assignment.id]['program'] = assignment.program if assignment.program is not None else ''
            assignment_condensed[assignment.id]['assignment_id'] = assignment.id if assignment.id is not None else ''
            assignment_condensed[assignment.id]['assignment_date'] = assignment.assignment_date if assignment.assignment_date is not None else ''
            assignment_condensed[assignment.id]['timestamp'] = timestamp = int(time.mktime(assignment.assignment_date.timetuple())) if assignment.assignment_date is not None else ''
            assignment_condensed[assignment.id]['assignment_priority'] = assignment.priority if assignment.priority is not None else ''
            assignment_condensed[assignment.id]['client_id'] = assignment.contact_id if assignment.contact_id is not None else ''
            assignment_condensed[assignment.id]['client_first_name'] = assignment.contact.first_name if assignment.contact.first_name is not None else ''
            assignment_condensed[assignment.id]['client_last_name'] = assignment.contact.last_name if assignment.contact.last_name is not None else ''
            assignment_condensed[assignment.id]['note'] = assignment.note if assignment.note is not None else ''
            assignment_condensed[assignment.id]['assigned_by_first_name'] = assignment.user.first_name if assignment.user.first_name is not None else ''
            assignment_condensed[assignment.id]['assigned_by_last_name'] = assignment.user.last_name if assignment.user.last_name is not None else ''
            # assignment_condensed[assignment.id]['assignment_status'] = assignment.assignment_status if assignment.assignment_status is not None else ''
            assignment_condensed[assignment.id]['instructor_first_name'] = assignment.instructor.first_name if assignment.instructor.first_name is not None else ''
            assignment_condensed[assignment.id]['instructor_last_name'] = assignment.instructor.last_name if assignment.instructor.last_name is not None else ''

            # Get the most recent notes of the most recent in-home plans
            # ==========================================================
            match assignment_condensed[assignment.id]['program']:
                case "SIP":
                    plans = getattr(assignment.contact, 'related_sipplans', [])
                    notes = getattr(assignment.contact, 'related_sipnotes', [])
                    # same as
                    # notes = assignment.contact.related_sipnotes
                    # but the above form is safer when there are no results
                case "1854":
                    plans = getattr(assignment.contact, 'related_sip1854plans', [])
                    # import pdb; pdb.set_trace()
                    notes = getattr(assignment.contact, 'related_sip1854notes', [])

            # Filter related_sipplans for "In-Home" where instructor_id matches SipPlan's user_id
            in_home_plans_for_assignee = [
                plan for plan in plans
                if      "In-home" in plan.plan_name
                    and plan.user_id == assignment.instructor_id

                    # HISTORICAL NOTE
                    #
                    # The note below was for `get_current_grant_year_startdate`
                    # (before switching to `get_current_date_minus_one_year`),
                    # and   I   remember   the  pain   of   getting   this
                    # one   right,  so   leaving   it   here  until   this
                    # whole   shebang  will   be  ripped   out.  I   think
                    # `get_current_date_minus_one_year` will get the right
                    # results,  but then  the whole  solution is  "ad hoc"
                    # given the current DB structure.
                    #
                    # > Every instructor has  one in-home plan per
                    # > grant year per client, but sometimes more,
                    # > so  show the  latest  one  in the  current
                    # > grant year

                    and plan.created.date() >= get_current_date_minus_one_year()

                    # FAILED ATTEMPS
                    #
                    # # 1. This will only pick plans for the grant year the assignment was created.
                    # and plan.created.date() >= date(assignment.assignment_date.year - 1, 10, 1)
                    # and plan.created.date() <= date(assignment.assignment_date.year, 9, 30)
                    #
                    # # 2. This won't work because of how different past plan names were...
                    # and datetime.strptime(plan.plan_name.split(' - ')[0], '%m/%d/%Y').date() >= assignment.assignment_date
            ]

            # import pdb; pdb.set_trace()

            if in_home_plans_for_assignee:
                # Find the most recent plan
                most_recent_in_home_for_assignee = max(in_home_plans_for_assignee, key=lambda plan: plan.created)
                assignment_condensed[assignment.id]['most_recent_in_home_id'] = most_recent_in_home_for_assignee.id

                notes_of_most_recent_in_home = [
                    note for note in notes
                    if      note.sip_plan_id == most_recent_in_home_for_assignee.id
                        # Subtracting  1 day  from  the assignment  date is  a
                        # quick and dirty workaround  for the fact that adding
                        # a new assignments sets the  assignment date 1 day in
                        # the future, breaking this conditional...
                        # TODO Figure out why assignment dates are saved 1 day ahead.
                        and note.note_date   >= (assignment.assignment_date - timedelta(days=1))
                ]
                if notes_of_most_recent_in_home:
                    most_recent_in_home_note = max(notes_of_most_recent_in_home, key=lambda note: note.note_date)
                    # import pdb; pdb.set_trace()
                    # Add details from most_recent_in_home_for_assignee to assignment_condensed
                    assignment_condensed[assignment.id]['most_recent_in_home_note_date'] = most_recent_in_home_note.note_date
                    assignment_condensed[assignment.id]['most_recent_in_home_note'] = most_recent_in_home_note.note
                    assignment_condensed[assignment.id]['most_recent_in_home_note_instructor'] = most_recent_in_home_note.instructor
                    # If there is a most recent in-home plan note,
                    # then its plan's id is the same as `most_recent_in_home_id`
                    # above.
                    # assignment_condensed[assignment.id]['most_recent_in_home_note_plan_id'] = most_recent_in_home_note.sip_plan_id
                else:
                    assignment_condensed[assignment.id]['most_recent_in_home_note_date']       = ''
                    assignment_condensed[assignment.id]['most_recent_in_home_note']            = ''
                    assignment_condensed[assignment.id]['most_recent_in_home_note_instructor'] = ''
                    # assignment_condensed[assignment.id]['most_recent_in_home_note_plan_id']    = ''
            else:
                assignment_condensed[assignment.id]['most_recent_in_home_note_date']       = ''
                assignment_condensed[assignment.id]['most_recent_in_home_note']            = ''
                assignment_condensed[assignment.id]['most_recent_in_home_note_instructor'] = ''
                # assignment_condensed[assignment.id]['most_recent_in_home_note_plan_id']    = ''
                assignment_condensed[assignment.id]['most_recent_in_home_id']              = ''

            # ==========================================================

            intakenotes = getattr(assignment.contact, 'related_intakenotes', [])
            # Again, same as above, but got burned by this form a couple times
            # intakenotes = assignment.contact.related_intakenotes

            # Filter related_sipplans for "In-Home" where instructor_id matches SipPlan's user_id
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

    # import pdb; pdb.set_trace()
    return render(request, 'lynx/instructor_search.html', {'filter': f, 'assignment_list': assignment_condensed})

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
    service_events = lm.OIBServiceEvent.objects.select_related(
        "oib_service_delivery_type",
        "entered_by"
    ).order_by("-date", "-id")
    return render(
        request,
        "lynx/oib/oib_service_event_list.html",
        {"service_events": service_events},
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
                'hx-trigger': 'mousedown',
                'hx-swap': 'innerHTML',
                'hx-target': 'this',
                # keep existing classes etc.
            })

        # empty_form: use __prefix__ placeholder so client-side add works
        empty = formset.empty_form
        if empty and 'client' in empty.fields:
            name = f"{formset.prefix}-__prefix__-client"
            q = f"?name={quote(name)}"
            empty.fields['client'].widget.attrs.update({
                'hx-get': base + q,
                'hx-trigger': 'mousedown',
                'hx-swap': 'innerHTML',
                'hx-target': 'this',
            })

    if request.method == 'POST':
        form = lfo.OIBServiceEventForm(request.POST)
        user_role_formset = OIBServiceEventUserRoleFormSet(request.POST, prefix=user_role_form_prefix)

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
        # GET request - show the form
        form = lfo.OIBServiceEventForm(initial=initial_data)
        user_role_formset = OIBServiceEventUserRoleFormSet(
            initial=user_role_initial, 
            prefix=user_role_form_prefix
        )
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
@login_required
def oib_plan_list(request, contact_id):
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

    return render(request, "lynx/oib/oib_plan_list.html", {
        "client": client,
        "plans": list(plans),
    })

def _current_oib_outcomes(contact_id, service_delivery_type_id, grant_year, *, return_ids=False):
    """
    Return dict: outcome_type_id -> (choice_label or choice_id)
    constrained to the given grant_year and service_delivery_type_id.
    Picks the newest (created desc) per type.
    """
    qs = (
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

    result = {}
    for o in qs:
        type_id = o.oib_outcome_type_choice.oib_outcome_type_id
        if type_id in result:
            continue  # already captured newest for this type
        choice_obj = o.oib_outcome_type_choice.oib_outcome_choice
        result[type_id] = choice_obj.id if return_ids else choice_obj.oib_outcome_choice
    return result

def _default_oib_outcome_choices_map():
    """
    Build a fallback map: outcome_type_id -> default choice label.
    Tries to infer by matching canonical strings; if not found picks first available choice.
    """
    wanted_labels = {
        "AT": "Not assessed",
        "IL/A": "Not assessed",
        "Living": "Plan not complete",
        "Home": "Plan not complete",
        "Employment": "Not Interested in Employment",
    }
    # Build per type
    defaults = {}
    for ot in lm.OIBOutcomeType.objects.all():
        choices = (
            lm.OIBOutcomeTypeChoice.objects
            .filter(oib_outcome_type=ot)
            .select_related('oib_outcome_choice')
        )
        label_match = None
        for otc in choices:
            lbl = otc.oib_outcome_choice.oib_outcome_choice
            # naive heuristic: look for a substring key
            for key, wanted in wanted_labels.items():
                if key.lower() in ot.oib_outcome_type.lower() and lbl == wanted:
                    label_match = lbl
                    break
            if label_match:
                break
        if not label_match and choices:
            label_match = choices.first().oib_outcome_choice.oib_outcome_choice
        defaults[ot.id] = label_match
    return defaults

def _default_oib_outcome_choice_ids_map():
    """
    Return dict outcome_type_id -> default oib_outcome_choice.id.
    Uses the same heuristics as _default_oib_outcome_choices_map but returns IDs
    so the edit form can preselect defaults when no current outcomes exist.
    """
    wanted_labels = {
        "AT": "Not assessed",
        "IL/A": "Not assessed",
        "Living": "Plan not complete",
        "Home": "Plan not complete",
        "Employment": "Not Interested in Employment",
    }
    defaults = {}
    for ot in lm.OIBOutcomeType.objects.all():
        qs = (
            lm.OIBOutcomeTypeChoice.objects
            .filter(oib_outcome_type=ot)
            .select_related('oib_outcome_choice')
        )
        chosen = None
        # try to match canonical label first
        for otc in qs:
            lbl = otc.oib_outcome_choice.oib_outcome_choice
            for key, wanted in wanted_labels.items():
                if key.lower() in ot.oib_outcome_type.lower() and lbl == wanted:
                    chosen = otc
                    break
            if chosen:
                break
        # fallback to first available choice
        if not chosen and qs.exists():
            chosen = qs.first()
        defaults[ot.id] = chosen.oib_outcome_choice.id if chosen else None
    return defaults

# NOTE 2025_09_30_2124 There are 5 rolling outcomes / client / grant year / service delivery type,
#                      which are not re-set when a new grant year starts. (The client wouldn't
#                      magically loose their progress just because a new grant year started.)
@login_required
def oib_plan_show(request, contact_id, grant_year, service_delivery_type_id):
    client = lm.Contact.objects.get(id=contact_id)
    service_delivery_type = lm.OIBServiceDeliveryType.objects.get(id=service_delivery_type_id)
    start_date = date(grant_year, 10, 1)
    end_date   = date(grant_year + 1, 9, 30)
    service_events = (
        lm.OIBServiceEvent.objects
        .filter(
            contacts__id=contact_id,
            oib_service_delivery_type__id=service_delivery_type_id,
            date__gte=start_date,
            date__lte=end_date
        )
        .order_by('-date')
    )

    outcome_types = lm.OIBOutcomeType.objects.all()
    current_map   = _current_oib_outcomes(contact_id, service_delivery_type_id, grant_year, return_ids=False)
    defaults_map  = _default_oib_outcome_choices_map()

    outcomes_display = []
    for ot in outcome_types:
        outcomes_display.append(
            (ot.oib_outcome_type, current_map.get(ot.id, defaults_map.get(ot.id)))
        )

    return render(request, "lynx/oib/oib_plan_show.html", {
        "client": client,
        "grant_year": grant_year,
        "service_delivery_type_id": service_delivery_type_id,
        "service_delivery_type_name": service_delivery_type.oib_service_delivery_type,
        "service_events": service_events,
        "outcomes_display": outcomes_display,
        "edit_mode": False,
    })

@login_required
def oib_plan_edit(request, contact_id, grant_year, service_delivery_type_id):
    client = lm.Contact.objects.get(id=contact_id)
    service_delivery_type = lm.OIBServiceDeliveryType.objects.get(id=service_delivery_type_id)
    start_date = date(grant_year, 10, 1)
    end_date   = date(grant_year + 1, 9, 30)
    service_events = (
        lm.OIBServiceEvent.objects
        .filter(
            contacts__id=contact_id,
            oib_service_delivery_type__id=service_delivery_type_id,
            date__gte=start_date,
            date__lte=end_date
        )
        .order_by('-date')
    )

    outcome_types = lm.OIBOutcomeType.objects.all()
    choices_by_type = {
        ot.id: list(
            lm.OIBOutcomeTypeChoice.objects
            .filter(oib_outcome_type=ot)
            .select_related('oib_outcome_choice')
            .order_by('oib_outcome_choice__oib_outcome_choice')
        )
        for ot in outcome_types
    }
    current_ids_map = _current_oib_outcomes(contact_id, service_delivery_type_id, grant_year, return_ids=True)
    defaults_ids_map = _default_oib_outcome_choice_ids_map()
    
    # Start with defaults, then override with any existing outcomes
    client_outcomes_map = {**defaults_ids_map, **(current_ids_map or {})}

    if request.method == "POST":
        for ot in outcome_types:
            choice_id = request.POST.get(f"outcome_{ot.id}")
            latest_choice_id = current_ids_map.get(ot.id)
            if choice_id and str(choice_id) != str(latest_choice_id):
                otc = lm.OIBOutcomeTypeChoice.objects.get(
                    oib_outcome_type=ot,
                    oib_outcome_choice_id=choice_id
                )
                lm.OIBOutcome.objects.create(
                    contact_id=contact_id,
                    oib_outcome_type_choice=otc,
                    user=request.user,
                    oib_service_delivery_type=service_delivery_type,
                    grant_year=grant_year
                )
        return redirect('lynx:oib_plan_show', contact_id, grant_year, service_delivery_type_id)

    return render(request, "lynx/oib/oib_plan_show.html", {
        "client": client,
        "grant_year": grant_year,
        "service_delivery_type_id": service_delivery_type_id,
        "service_delivery_type_name": service_delivery_type.oib_service_delivery_type,
        "service_events": service_events,
        "outcome_types": outcome_types,
        "choices_by_type": choices_by_type,
        "client_outcomes_map": client_outcomes_map,
        "edit_mode": True,
    })

# vim: set foldmethod=marker foldmarker={{-,}}-:
