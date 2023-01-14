import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView

from .forms import LessonNoteForm
from .models import (Contact, Address, Phone, Email, Intake, IntakeNote, EmergencyContact, Authorization,
                     ProgressReport, LessonNote, SipNote, Volunteer, SipPlan, Vaccine, Assignment)
from .support_functions import get_fiscal_year, get_quarter

logger = logging.getLogger(__name__)


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
              'hire_date', 'payment_source', 'referred_by', 'communication', 'communication_notes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["other_languages"].label = "Other Language(s)"
        form.fields["other_ethnicity"].label = "Ethnicity (if other)"
        form.fields['payment_source'].queryset = Contact.objects.filter(payment_source=1).order_by(Lower('last_name'))
        form.fields['payment_source'].label = "Payment Sources"
        form.fields["crime"].label = "Have you been convicted of a crime?"
        form.fields["crime_info"].label = \
            "If yes, what and when did the convictions occur? What county did this conviction occur in?"
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
    fields = ['name', 'emergency_notes', 'relationship']
    template_name_suffix = '_edit'


class LessonNoteUpdateView(LoginRequiredMixin, UpdateView):
    form_class = LessonNoteForm
    model = LessonNote
    template_name_suffix = '_edit'


class ProgressReportUpdateView(LoginRequiredMixin, UpdateView):
    model = ProgressReport
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
        form.fields[
            "short_term_goals_time"].label = "Estimated number of Hours needed for completion of short term objectives"
        form.fields["long_term_goals"].label = "Remaining Long Term Objectives"
        form.fields[
            "long_term_goals_time"].label = "Estimated number of Hours needed for completion of long term objectives"
        return form


class SipNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = SipNote
    fields = ['note', 'note_date', 'at_devices', 'independent_living', 'orientation', 'communications', 'dls',
              'support', 'advocacy', 'counseling', 'information', 'services', 'retreat', 'in_home', 'seminar',
              'modesto', 'group', 'community', 'class_hours', 'sip_plan', 'instructor']
    template_name_suffix = '_edit'

    def form_valid(self, form):
        post = form.save(commit=False)
        note_date = post.note_date
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
        action = "/lynx/client/" + str(post.contact_id)
        return HttpResponseRedirect(action)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
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
        return form


class SipPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = SipPlan
    fields = ['note', 'at_services', 'independent_living', 'orientation', 'communications', 'dls', 'advocacy',
              'counseling', 'information', 'other_services', 'plan_name', 'living_plan_progress', 'at_outcomes',
              'community_plan_progress', 'ila_outcomes', 'support_services', 'plan_date']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        notes = SipNote.objects.filter(sip_plan_id=self.kwargs['pk'])
        ils = True
        ats = True
        outcomes = True
        for note in notes:
            if note.orientation or note.communications or note.dls or note.advocacy or note.counseling \
                    or note.information or note.services or note.support:
                ils = False
            if note.at_devices or note.at_services:
                ats = False
        if not ils or not ats:
            outcomes = False
        form = super().get_form(form_class=form_class)
        form.fields['at_services'].label = "Assistive Technology Devices and Services"
        form.fields['independent_living'].label = "Independent Living and Adjustment Services"
        form.fields['orientation'].label = "Orientation & Mobility Training"
        form.fields['communications'].label = "Communication Skills Training"
        form.fields['dls'].label = "Daily Living Skills Training"
        form.fields['plan_date'].label = "Start Date"
        form.fields['advocacy'].label = "Advocacy Training"
        form.fields['information'].label = "Information and Referral"
        form.fields['counseling'].label = "Adjustment Counseling"
        form.fields['support_services'].label = "Supportive Services"
        form.fields['other_services'].label = "Other IL/A Services"
        form.fields['living_plan_progress'].label = "Living Situation Outcomes"
        form.fields['community_plan_progress'].label = "Home and Community involvement Outcomes"
        form.fields['at_outcomes'].label = "AT Goal Outcomes"
        form.fields['ila_outcomes'].label = "IL/A Service Goal Outcomes"

        form.fields['at_outcomes'].disabled = ats
        form.fields['ila_outcomes'].disabled = ils
        form.fields['living_plan_progress'].disabled = outcomes
        form.fields['community_plan_progress'].disabled = outcomes
        return form


class AuthorizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Authorization
    fields = ['intake_service_area', 'authorization_number', 'authorization_type', 'start_date', 'end_date',
              'total_time', 'billing_rate', 'outside_agency', 'student_plan', 'notes']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['outside_agency'].queryset = Contact.objects.filter(payment_source=1).order_by(Lower('last_name'))
        form.fields['outside_agency'].label = "Payment Sources"
        form.fields['start_date'].label = "Start Date (YYYY-MM-DD)"
        form.fields['end_date'].label = "End Date (YYYY-MM-DD)"
        return form


class VolunteerHourUpdateView(LoginRequiredMixin, UpdateView):
    model = Volunteer
    fields = ['volunteer_type', 'note', 'volunteer_date', 'volunteer_hours']
    template_name_suffix = '_edit'


class VaccineUpdateView(LoginRequiredMixin, UpdateView):
    model = Vaccine
    fields = ['vaccine', 'vaccine_note', 'vaccination_date']
    template_name_suffix = '_edit'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['vaccine'].label = "Type"
        form.fields['vaccine_note'].label = "Notes"
        form.fields['vaccination_date'].label = "Date"
        return form


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    fields = ['note', 'assignment_status']
    template_name_suffix = '_edit'
