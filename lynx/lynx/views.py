from datetime    import datetime, date, timedelta
from django      import forms
from django.apps import apps
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins     import LoginRequiredMixin  \
                                         , UserPassesTestMixin

from django.contrib.auth import models as dca

from django.core.mail      import send_mail
from django.core.paginator import Paginator

from django.db        import connection
from django.db        import models    as ddm
from django.db.models import functions as ddmf

from django.forms.models  import model_to_dict
from django.http          import HttpResponse         \
                               , HttpResponseRedirect \
                               , Http404              \
                               , JsonResponse
from django.shortcuts     import render  \
                               , reverse \
                               , redirect
from django.urls          import reverse_lazy
from django.views.generic import DetailView   \
                               , DeleteView   \
                               , TemplateView \
                               , UpdateView

import csv, logging, os, re, time

# lm  = lynx model
# lfo = lynx form
# lfi = lynx filter
from . import models  as lm  \
            , forms   as lfo \
            , filters as lfi

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
def volunteer_list_view(request):
    volunteers = lm.Contact.objects.filter(volunteer_check=1).order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name'))
    return render(request, 'lynx/volunteer_list.html', {'volunteers': volunteers})


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
    # import pdb; pdb.set_trace()

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
def add_contact(request):
    form = lfo.ContactForm()
    address_form = lfo.AddressForm()
    phone_form = lfo.PhoneForm()
    email_form = lfo.EmailForm()
    if request.method == 'POST':
        form = lfo.ContactForm(request.POST)
        address_form = lfo.AddressForm(request.POST)
        phone_form = lfo.PhoneForm(request.POST)
        email_form = lfo.EmailForm(request.POST)
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
    form = lfo.IntakeForm()
    if request.method == 'POST':
        form = lfo.IntakeForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user_id = request.user.id
            form.contact_id = contact_id
            form.active = 1
            form.save()
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
    return render(request, 'lynx/add_intake.html', {'form': form})


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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))

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
def add_sip_note_bulk(request):
    form = lfo.SipNoteBulkForm()
    client_list = lm.Contact.objects.filter(sip_client=1).order_by(ddmf.Lower('last_name'))
    range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if request.method == 'POST':
        form = lfo.SipNoteBulkForm(request.POST)
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


@login_required
def add_sip1854_note_bulk(request):
    form = lfo.Sip1854NoteBulkForm()
    client_list = lm.Contact.objects.filter(sip_client=1).order_by(ddmf.Lower('last_name'))
    range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if request.method == 'POST':
        form = lfo.Sip1854NoteBulkForm(request.POST)
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
    return render(request, 'lynx/add_sip1854_note_bulk.html', {'form': form, 'client_list': client_list, 'range': range})


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

            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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


# TODO aside from some classes, the code is the same as `add_contact`
@login_required
def add_volunteer(request):
    form = lfo.VolunteerForm()
    contact_form = lfo.ContactForm()
    address_form = lfo.AddressForm()
    phone_form = lfo.PhoneForm()
    email_form = lfo.EmailForm()
    if request.method == 'POST':
        form = lfo.VolunteerForm(request.POST)
        contact_form = lfo.ContactForm(request.POST)
        address_form = lfo.AddressForm(request.POST)
        phone_form = lfo.PhoneForm(request.POST)
        email_form = lfo.EmailForm(request.POST)
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
    form = lfo.VolunteerHoursForm()
    if request.method == 'POST':
        form = lfo.VolunteerHoursForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            contact_id = form.contact_id
            form.user_id = request.user.id
            form.save()
            return HttpResponseRedirect(reverse('lynx:volunteer', args=(contact_id,)))
    return render(request, 'lynx/add_volunteer_hours.html', {'form': form})


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
            return HttpResponseRedirect(reverse('lynx:client', args=(contact_id,)))
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
def volunteers_report_month(request):
    form = lfo.VolunteerReportForm()
    if request.method == 'POST':
        form = lfo.VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = lm.Volunteer.objects.raw("""SELECT lc.id, CONCAT(lc.last_name, ', ', lc.first_name) as name,
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
    form = lfo.VolunteerReportForm()
    if request.method == 'POST':
        form = lfo.VolunteerReportForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            start = data.get('start_date')
            end = data.get('end_date')
            volunteers = lm.Volunteer.objects.raw("""SELECT lc.id,
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
    return render(request, 'lynx/client_search.html', {'object_list': object_list, 'clients': clients})


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

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = lm.Contact

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContactDetailView, self).get_context_data(**kwargs)
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

        return context

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
            action = "/lynx/client/" + str(self.kwargs['pk'])
            return HttpResponseRedirect(action)


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


class VolunteerDetailView(LoginRequiredMixin, DetailView):
    model = lm.Contact
    template_name = 'lynx/volunteer_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VolunteerDetailView, self).get_context_data(**kwargs)
        context['volunteer_list'] = lm.Volunteer.objects.filter(contact_id=self.kwargs['pk'])
        context['address_list'] = lm.Address.objects.filter(contact_id=self.kwargs['pk'])
        context['phone_list'] = lm.Phone.objects.filter(contact_id=self.kwargs['pk'])
        context['email_list'] = lm.Email.objects.filter(contact_id=self.kwargs['pk'])
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Contact
    fields = ['first_name', 'middle_name', 'last_name', 'company', 'do_not_contact', 'donor', 'deceased',
              'remove_mailing', 'active', 'contact_notes', 'sip_client', 'core_client', 'sip1854_client', 'careers_plus',
              'careers_plus_youth', 'volunteer_check', 'access_news', 'other_services']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["volunteer_check"].label = "Volunteer"
        form.fields["sip1854_client"].label = "18-54 client"
        return form


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


class VolunteerHourUpdateView(LoginRequiredMixin, UpdateView):
    model = lm.Volunteer
    fields = ['volunteer_type', 'note', 'volunteer_date', 'volunteer_hours']
    template_name_suffix = '_edit'


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
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


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
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class ContactDeleteView(UserPassesTestMixin, DeleteView):
    model = lm.Contact

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('lynx:index')


class LessonNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.LessonNote

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class VolunteerHourDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Volunteer

    def get_success_url(self):
        return reverse_lazy('lynx:volunteer_list')


class PhoneDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Phone

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class VaccineDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Vaccine

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = lm.Document

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


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

            with connection.cursor() as cursor:
                cursor.execute("""SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, int.intake_date as date, int.age_group, int.gender, int.ethnicity,
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
                query = """SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, ls.fiscal_year,
                ls.vision_screening, ls.treatment, ls.at_devices, ls.at_services, ls.orientation, ls.communications,
                ls.dls, ls.support, ls.advocacy, ls.counseling, ls.information, ls.services, addr.county, ls.note_date,
                ls.independent_living, sp.living_plan_progress, sp.community_plan_progress, sp.ila_outcomes,
                sp.at_outcomes, ls.class_hours
                    FROM lynx_sipnote as ls
                    left JOIN lynx_contact as c on c.id = ls.contact_id
                    inner join lynx_address as addr on c.id= addr.contact_id
                    left JOIN lynx_sipplan as sp on sp.id = ls.sip_plan_id
                    where  fiscal_year = '%s'
                    and quarter <= %d
                    and c.sip_client is true
                    order by c.last_name, c.first_name;""" % (fiscal_year, int(quarter))
                                                                                      #, int(quarter), fiscal_year)
                # and c.id not in (SELECT contact_id FROM lynx_sipnote AS sip WHERE quarter < %d and fiscal_year = '%s')
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
                    ila_outcomes = aggregated_data[client_id][quarter]['ila_outcomes']
                    at_outcomes = aggregated_data[client_id][quarter]['at_outcomes']
                    aggregated_data[client_id][quarter]['assessed'] = is_assessed(ila_outcomes, at_outcomes)
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
                    if note['ila_outcomes'] and note['at_outcomes']:
                        aggregated_data[client_id][quarter]['assessed'] = is_assessed(
                            aggregated_data[client_id][quarter]['ila_outcomes'],
                            aggregated_data[client_id][quarter]['at_outcomes'])

            for key, value in aggregated_data.items():
                if '1' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['1']['at_devices_services'], "", "", value['1']['at_outcomes'], "",
                                     value['1']['independent_living'], value['1']['orientation'],
                                     value['1']['communications'], value['1']['dls'], value['1']['advocacy'],
                                     value['1']['counseling'], value['1']['information'], value['1']['services'],
                                     value['1']['ila_outcomes'], "", value['1']['support'], value['1']['assessed'],
                                     value['1']['living_plan_progress'], value['1']['community_plan_progress']])
                if '2' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['2']['at_devices_services'], "", "", value['2']['at_outcomes'], "",
                                     value['2']['independent_living'], value['2']['orientation'],
                                     value['2']['communications'], value['2']['dls'], value['2']['advocacy'],
                                     value['2']['counseling'], value['2']['information'], value['2']['services'],
                                     value['2']['ila_outcomes'], "", value['2']['support'], value['2']['assessed'],
                                     value['2']['living_plan_progress'], value['2']['community_plan_progress']])
                if '3' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['3']['at_devices_services'], "", "", value['3']['at_outcomes'], "",
                                     value['3']['independent_living'], value['3']['orientation'],
                                     value['3']['communications'], value['3']['dls'], value['3']['advocacy'],
                                     value['3']['counseling'], value['3']['information'], value['3']['services'],
                                     value['3']['ila_outcomes'], "", value['3']['support'], value['3']['assessed'],
                                     value['3']['living_plan_progress'], value['3']['community_plan_progress']])
                if '4' in value:
                    writer.writerow([value['client_name'], "0", "", "", "", "", "",
                                     value['4']['at_devices_services'], "", "", value['4']['at_outcomes'], "",
                                     value['4']['independent_living'], value['4']['orientation'],
                                     value['4']['communications'], value['4']['dls'], value['4']['advocacy'],
                                     value['4']['counseling'], value['4']['information'], value['4']['services'],
                                     value['4']['ila_outcomes'], "", value['4']['support'], value['4']['assessed'],
                                     value['4']['living_plan_progress'], value['4']['community_plan_progress']])

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
                cursor.execute("""SELECT CONCAT(c.last_name, ', ', c.first_name) as name, c.id as id, int.age_group,
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
                    if client["ethnicity"] == "Hispanic or Latino" or client["other_ethnicity"] == "Hispanic or Latino" or client["ethnicity"] == "Two or More Races" or client["other_ethnicity"] == "Two or More Races":
                        client["hispanic"] = "Yes"
                        client["race"] = "2 or More Races"
                        hispanic = True

                    if client["other_ethnicity"] or hispanic:
                        client["race"] = "2 or More Races"
                    elif client["ethnicity"] == "Other":
                        client["race"] = "Did not self identify Race"
                    elif client["ethnicity"] == "Two or More Races":
                        client["race"] = "2 or More Races"
                    else:
                        client["race"] = client["ethnicity"]

                    #Sort out degree of impairment
                    if client['degree'] == "Totally Blind (NP or NLP)":
                        client['degree'] = "Totally Blind"
                    elif client['degree'] == "Legally Blind":
                        client['degree'] = "Legally Blind"
                    else:
                        client['degree'] = "Severe Vision Impairment"

                    #Sort out cause
                    ok_diagnosis = ["Cataracts", "Diabetic Retinopathy", "Glaucoma", "Macular Degeneration"]
                    if client['eye_condition'] not in ok_diagnosis:
                        client['eye_condition'] = "Other causes of visual impairment"

                    #Sort out residence
                    if client['residence_type'] == "Community Residential":
                        client['residence_type'] = "Senior Independent Living"
                    if client['residence_type'] == "Assisted Living":
                        client['residence_type'] = "Assisted Living Facility"
                    if client['residence_type'] == "Skilled Nursing Care":
                        client['residence_type'] = "Nursing Home"
                    if client['residence_type'] == "Senior Living":
                        client['residence_type'] = "Senior Independent Living"
                    if client['residence_type'] == "Private Residence - apartment or home (alone, or with roommate, personal care assistant, family, or other person)":
                        client['residence_type'] = "Private Residence"

                    #sort of referral
                    ok_sources = ["Veterans Administration", "Family or Friend", "Senior Program", "Assisted Living Facility",
                                  "Nursing Home", "Independent Living Center", "Self-Referral", "Eye Care Provider",
                                  "Physician/ Medical Provider"]
                    if client['referred_by'] == "DOR" or client['referred_by'] == "Alta":
                        client['referred_by'] = "State VR Agency"
                    elif client['referred_by'] == "Physician":
                        client['referred_by'] = "Physician/ Medical Provider"
                    elif client['referred_by'] not in ok_sources:
                        client['referred_by'] = "Other"


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
        f = lfi.ContactFilter(request.GET, queryset=lm.ContactInfoView.objects.all().order_by(ddmf.Lower('full_name')))

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
                    client_condensed[client.id]['bad_address'] = client_condensed[client.id]['bad_address'] + ', ' + str(client.bad_address)
                if client_condensed[client.id]['do_not_contact'] != client.do_not_contact and client.do_not_contact is not None:
                    client_condensed[client.id]['do_not_contact'] = client_condensed[client.id]['do_not_contact'] + ', ' + str(client.do_not_contact)
                if client_condensed[client.id]['remove_mailing'] != client.remove_mailing and client.remove_mailing is not None:
                    client_condensed[client.id]['remove_mailing'] = client_condensed[client.id]['remove_mailing'] + ', ' + str(client.remove_mailing)
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
                client_condensed[client.id]['bad_address'] = str(client.bad_address) if client.bad_address is not None else ''
                client_condensed[client.id]['do_not_contact'] = str(client.do_not_contact) if client.do_not_contact is not None else ''
                client_condensed[client.id]['deceased'] = str(client.deceased) if client.deceased is not None else ''
                client_condensed[client.id]['remove_mailing'] = str(client.remove_mailing) if client.remove_mailing is not None else ''
                client_condensed[client.id]['active'] = str(client.active) if client.active is not None else ''
                client_condensed[client.id]['sip_client'] = str(client.sip_client) if client.sip_client is not None else ''
                client_condensed[client.id]['core_client'] = str(client.core_client) if client.core_client is not None else ''
                client_condensed[client.id]['sip1854_client'] = str(client.sip1854_client) if client.sip1854_client is not None else ''

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
                client['sip1854_client'] = "18-54 Client" if client['sip1854_client'] is not None else ''
                client['remove_mailing'] = "Remove from Mailing List" if client['remove_mailing'] is not None else ''

                writer.writerow(
                    [client['full_name'], client['first_name'], client['last_name'], client['intake_date'],
                     client['age_group'], client['county'], client['email'], client['full_phone'],
                     client['address_one'], client['address_two'], client['suite'], client['city'], client['state'],
                     client['zip_code'], client['region'], client['bad_address'], client['do_not_contact'],
                     client['deceased'], client['remove_mailing'], client['active'], client['sip_client'],
                     client['core_client'], client['sip1854_client']])
            return response

    else:
        f = lfi.ContactFilter()
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


# vim: set foldmethod=marker foldmarker={{-,}}-:
