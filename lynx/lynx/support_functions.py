import csv
import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q, F
from django.db.models import Value as V
from django.db.models.functions import Concat, Replace, Lower
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView, DeleteView, TemplateView
from django.views.generic.edit import UpdateView

from .filters import AssignmentFilter, ContactFilter
from .forms import (ContactForm, IntakeForm, IntakeNoteForm, EmergencyForm, AddressForm, EmailForm, PhoneForm,
                    AuthorizationForm, ProgressReportForm, LessonNoteForm, SipNoteForm, BillingReportForm,
                    SipDemographicReportForm, VolunteerForm, SipCSFReportForm, SipPlanForm, SipNoteBulkForm,
                    DocumentForm, VolunteerHoursForm, VolunteerReportForm, VaccineForm, AssignmentForm)
from .models import (Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization,
                     ProgressReport, LessonNote, SipNote, Volunteer, SipPlan, ContactInfoView, Document, Vaccine,
                     Assignment)

logger = logging.getLogger(__name__)



def get_hour_validation(request, authorization_id,
                        billed_units):  # check if they are entering more hours then allowed on authorization
    authorization = Authorization.objects.get(id=authorization_id)
    note_list = LessonNote.objects.filter(authorization_id=authorization_id)

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


def get_date_validation(request, authorization_id,
                        note_date):  # check if they are entering a lesson note after the authorization authorization
    authorization = Authorization.objects.get(id=authorization_id)
    auth_date = authorization.end_date
    auth_date = auth_date.strftime("%Y-%m-%d")

    if note_date > auth_date:
        return JsonResponse({"result": 'false'})
    else:
        return JsonResponse({"result": 'true'})


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
