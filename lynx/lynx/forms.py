from django import forms
from django.db.models.functions import Lower
from django.utils import timezone
from django.db.models import Q, F
from django.db.models import Value as V
from django.db.models import DateField
from django.forms.models import ModelChoiceField
from django.db.models.functions import Concat, Replace, Lower, Substr, StrIndex, Cast

from .models import Contact, Address, Intake, Email, Phone, SipPlan, Sip1854Plan, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Sip1854Note, Volunteer, UNITS, Document, Vaccine, Assignment

from datetime import datetime

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"),
          ('all', 'All Months'))

quarters = (("1", "Q1"), ("2", "Q2"), ("3", "Q3"), ("4", "Q4"))


class ContactForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['volunteer_check'].label = "Volunteer"


class IntakeForm(forms.ModelForm):
    intake_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Intake Date', initial=timezone.now())
    birth_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Birth Date', initial=timezone.now())
    eye_condition_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Onset date of eye condition', initial=timezone.now())
    hire_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Hire Date', initial=timezone.now())


    class Meta:
        model = Intake
        exclude = ('contact', 'created', 'modified', 'user')
        widgets = {
            # "intake_date": forms.DateInput(attrs={'type': 'date'}),
            # "birth_date":  forms.DateInput(attrs={'type': 'date'}),
            # "eye_condition_date":  forms.DateInput(attrs={'type': 'date'}),
            # "hire_date":  forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(IntakeForm, self).__init__(*args, **kwargs)
        self.fields['intake_date'].label = "Intake Date (YYYY-MM-DD)"
        self.fields['payment_source'].queryset = Contact.objects.filter(payment_source=1).order_by(Lower('last_name'))
        self.fields['payment_source'].label = "Payment Sources"
        self.fields['eye_condition_date'].label = "Eye Condition Onset Date (YYYY-MM-DD)"
        self.fields['birth_date'].label = "Birthdate (YYYY-MM-DD)"
        self.fields['other_languages'].label = "Other Language(s)"
        self.fields['ethnicity'].label = "Race"
        self.fields['other_ethnicity'].label = "Ethnicity"
        self.fields['crime'].label = "Have you been convicted of a crime?"
        self.fields['crime_info'].label = "Criminal Details"
        self.fields['crime_other'].label = "Criminal Conviction Information"
        self.fields['parole'].label = "Are you on parole?"
        self.fields['parole_info'].label = "Parole Information"
        self.fields['crime_history'].label = "Additional Criminal History"
        self.fields['musculoskeletal'].label = "Musculoskeletal Disorders"
        self.fields['alzheimers'].label = "Alzheimer’s Disease/Cognitive Impairment"
        self.fields['medical_notes'].label = "Medical History"
        self.fields['hobbies'].label = "Hobbies/Interests"
        self.fields['high_bp'].label = "Hypertension"
        self.fields['high_bp_notes'].label = "Hypertension Notes"
        self.fields['geriatric'].label = "Other Major Geriatric Concerns"
        self.fields['degree'].label = "Degree of Vision Loss"
        self.fields['secondary_eye_condition'].label = "Secondary Eye Condition"
        self.fields['heart'].label = "Cardiovascular Disease"
        self.fields['heart_notes'].label = "Cardiovascular Disease Notes"
        self.fields['dexterity'].label = "Use of Hands, Arms, and Fingers"
        self.fields['dexterity_notes'].label = "Use of Hands, Arms, and Fingers Notes"
        self.fields['migraine'].label = "Migraine Headache"
        self.fields['memory_loss'].label = "Memory Loss/Tension"
        self.fields['memory_loss_notes'].label = "Memory Loss/Tension Notes"
        self.fields['communication'].label = "Communication Impairments"
        self.fields['communication_notes'].label = "Communication Impairment Notes"


class AddressForm(forms.ModelForm):

    class Meta:

        model = Address
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['suite'].label = "Apt/Suite"


class EmergencyForm(forms.ModelForm):

    class Meta:

        model = EmergencyContact
        exclude = ('created', 'modified', 'user', 'contact')


class EmailForm(forms.ModelForm):

    class Meta:

        model = Email
        exclude = ('created', 'modified', 'user', 'contact', 'active', 'emergency_contact')


class PhoneForm(forms.ModelForm):

    class Meta:

        model = Phone
        exclude = ('created', 'modified', 'user', 'contact', 'active', 'emergency_contact')


class IntakeNoteForm(forms.ModelForm):

    class Meta:

        model = IntakeNote
        fields = ('note',)


class AuthorizationForm(forms.ModelForm):
    start_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Start Date', initial=timezone.now())
    end_date   = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='End Date', initial=timezone.now())

    class Meta:

        model = Authorization
        exclude = ('created', 'modified', 'user', 'contact')
        widgets = {
            # "start_date": forms.DateInput(attrs={'type': 'date'}),
            # "end_date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['outside_agency'].queryset = Contact.objects.filter(payment_source=1).order_by(Lower('last_name'))
        self.fields['outside_agency'].label = "Payment Sources"
        self.fields['start_date'].label = "Start Date (YYYY-MM-DD)"
        self.fields['end_date'].label = "End Date (YYYY-MM-DD)"


class ProgressReportForm(forms.ModelForm):

    class Meta:

        model = ProgressReport
        exclude = ('created', 'modified', 'user', 'authorization')

    def __init__(self, *args, **kwargs):
        super(ProgressReportForm, self).__init__(*args, **kwargs)
        self.fields['instructor'].label = "Instructor(s)"
        self.fields['accomplishments'].label = "Client Accomplishments"
        self.fields['client_behavior'].label = "The client's attendance, attitude, and motivation during current month"
        self.fields['short_term_goals'].label = "Remaining Short Term Objectives"
        self.fields['short_term_goals_time'].label = "Estimated number of Hours needed for completion of short term objectives"
        self.fields['long_term_goals'].label = "Remaining Long Term Objectives"
        self.fields['long_term_goals_time'].label = "Estimated number of Hours needed for completion of long term objectives"
        self.fields['notes'].label = "Additional comments"


class LessonNoteForm(forms.ModelForm):
    total_time = forms.CharField(required=False)
    total_used = forms.CharField(required=False)
    billed_units = forms.ChoiceField(choices=UNITS, widget=forms.Select(attrs={"onChange": 'checkHours(this)'}))
    date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Lesson date', initial=timezone.now())

    class Meta:
        model = LessonNote
        exclude = ('created', 'modified', 'user')
        widgets = {
            # "date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(LessonNoteForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = "Lesson Note Date (YYYY-MM-DD)"


# class CustomModelChoiceField(ModelChoiceField):
#     def __init__(self, *args, **kwargs):
#         # Define additional choices
#         self.additional_choices = [
#               ('In-home',               'Add new In-home plan')
#             , ('Support Group',         'Add new Support Group plan')
#             , ('Training Seminar',      'Add new Training Seminar plan')
#           # , ('Workshop',              'Add new Workshop plan')
#             , ('Community Integration', 'Add new Community Integration plan')
#             , ('Retreat',               'Add new Retreat plan')
#             ]
#         super(CustomModelChoiceField, self).__init__(*args, **kwargs)
#         # Prepend additional choices to the field choices
#         self.choices = self.additional_choices + list(self.choices)
#
#     def label_from_instance(self, obj):
#         # Custom label formatting can be done here
#         return super(CustomModelChoiceField, self).label_from_instance(obj)


class BasePlanNoteForm(forms.ModelForm):
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)
    note_date = forms.DateField(widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Note Date', initial=timezone.now())

    class Meta:
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')
        widgets = {
            # "note_date": forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id')
        plan_id = kwargs.pop('plan_id', None)
        super(BasePlanNoteForm, self).__init__(*args, **kwargs)
        self.fields['sip_plan'].queryset = self.get_plan_queryset(contact_id)
        self.fields['sip_plan'].required = True
        self.fields['at_devices'].label = "Assistive Technology Devices and Services"
        self.fields['independent_living'].label = "Independent Living and Adjustment Services"
        self.fields['orientation'].label = "Orientation & Mobility Training"
        self.fields['communications'].label = "Communication Skills Training"
        self.fields['dls'].label = "Daily Living Skills Training"
        self.fields['support'].label = "Supportive Services"
        self.fields['advocacy'].label = "Advocacy Training"
        self.fields['information'].label = "Information and Referral"
        self.fields['services'].label = "Other IL/A Services"
        self.fields['in_home'].label = "In-home training"
        self.fields['seminar'].label = "Training Seminar"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"
        self.fields['class_hours'].required = True
        self.fields['instructor'].label = "Instructor"
        self.fields['note_date'].required = True
        if plan_id:
            self.fields['sip_plan'].initial = plan_id

    def get_plan_queryset(self, contact_id):
        raise NotImplementedError("Subclasses should implement this method.")


class SipNoteForm(BasePlanNoteForm):
    class Meta(BasePlanNoteForm.Meta):
        model = SipNote

    def get_plan_queryset(self, contact_id):
        return SipPlan.objects.filter(contact_id=contact_id).annotate(
            date_substring=Cast(Substr('plan_name', 1, StrIndex('plan_name', V(' '))), DateField())
        ).order_by('-date_substring')


class Sip1854NoteForm(BasePlanNoteForm):
    class Meta(BasePlanNoteForm.Meta):
        model = Sip1854Note

    def get_plan_queryset(self, contact_id):
        return Sip1854Plan.objects.filter(contact_id=contact_id).annotate(
            date_substring=Cast(Substr('plan_name', 1, StrIndex('plan_name', V(' '))), DateField())
        ).order_by('-date_substring')


class SipNoteBulkForm(forms.ModelForm):
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)
    note_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Note Date', initial=timezone.now())

    class Meta:
        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')
        widgets = {
            # "note_date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(SipNoteBulkForm, self).__init__(*args, **kwargs)
        self.fields['at_devices'].label = "Assistive Technology Devices and Services"
        self.fields['independent_living'].label = "Independent Living and Adjustment Services"
        self.fields['orientation'].label = "Orientation & Mobility Training"
        self.fields['communications'].label = "Communication Skills Training"
        self.fields['dls'].label = "Daily Living Skills Training"
        self.fields['support'].label = "Supportive Services"
        self.fields['advocacy'].label = "Advocacy Training"
        self.fields['information'].label = "Information and Referral"
        self.fields['services'].label = "Other IL/A Services"
        self.fields['in_home'].label = "In-home training"
        self.fields['seminar'].label = "Training Seminar"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"
        self.fields['instructor'].label = "Instructor"
        self.fields['sip_plan'].label = "SIP Plan"


class Sip1854NoteBulkForm(forms.ModelForm):
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)
    note_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Note Date', initial=timezone.now())

    class Meta:
        model = Sip1854Note
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')
        widgets = {
            # "note_date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(Sip1854NoteBulkForm, self).__init__(*args, **kwargs)
        self.fields['at_devices'].label = "Assistive Technology Devices and Services"
        self.fields['independent_living'].label = "Independent Living and Adjustment Services"
        self.fields['orientation'].label = "Orientation & Mobility Training"
        self.fields['communications'].label = "Communication Skills Training"
        self.fields['dls'].label = "Daily Living Skills Training"
        self.fields['support'].label = "Supportive Services"
        self.fields['advocacy'].label = "Advocacy Training"
        self.fields['information'].label = "Information and Referral"
        self.fields['services'].label = "Other IL/A Services"
        self.fields['in_home'].label = "In-home training"
        self.fields['seminar'].label = "Training Seminar"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"
        self.fields['instructor'].label = "Instructor"
        self.fields['sip_plan'].label = "SIP Plan"


class BasePlanForm(forms.ModelForm):
    types = ( ("In-home", "In-home")                             \
            , ("Support Group", "Support Group")                 \
            , ("Training Seminar", "Training Seminar")           \
          # , ("Workshop", "Workshop")                           \
            , ("Community Integration", "Community Integration") \
            , ("Retreat", "Retreat")                             \
            )

    instructor = forms.CharField(required=False)
    plan_type = forms.ChoiceField(choices=types)
    plan_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Plan Date', initial=timezone.now())

    def __init__(self, *args, **kwargs):
        super(BasePlanForm, self).__init__(*args, **kwargs)
        self.fields['at_services'].label = "Assistive Technology Devices and Services"
        self.fields['independent_living'].label = "Independent Living and Adjustment Services"
        self.fields['orientation'].label = "Orientation & Mobility Training"
        self.fields['communications'].label = "Communication Skills Training"
        self.fields['dls'].label = "Daily Living Skills Training"
        self.fields['plan_date'].label = "Start Date"
        self.fields['advocacy'].label = "Advocacy Training"
        self.fields['information'].label = "Information and Referral"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['support_services'].label = "Supportive Services"
        self.fields['other_services'].label = "Other IL/A Services"
        self.fields['living_plan_progress'].label = "Living Situation Outcome"
        self.fields['community_plan_progress'].label = "Home and Community Involvement Outcome"
        self.fields['at_outcomes'].label = "AT Goal Outcomes"
        self.fields['ila_outcomes'].label = "IL/A Service Goal Outcome"

    class Meta:
        model = None  # Placeholder, to be overridden
        exclude = ('created', 'modified', 'user', 'contact')

class SipPlanForm(BasePlanForm):
    class Meta(BasePlanForm.Meta):
        model = SipPlan

class Sip1854PlanForm(BasePlanForm):
    class Meta(BasePlanForm.Meta):
        model = Sip1854Plan


class BillingReportForm(forms.Form):
    current_year = datetime.now().year
    old_year = current_year - 20
    high_year = current_year + 2

    years = []
    for x in range(old_year, high_year):
        year_str = str(x)
        year_pair = (year_str, year_str)
        years.append(year_pair)

    month = forms.ChoiceField(choices=months)
    year = forms.ChoiceField(choices=years)

    def __init__(self, *args, **kwargs):
        super(BillingReportForm, self).__init__(*args, **kwargs)
        current_year = datetime.now().year
        self.initial['year'] = str(current_year)


class SipDemographicReportForm(forms.Form):
    current_year = datetime.now().year
    old_year = current_year - 20
    high_year = current_year + 2

    years = []
    for x in range(old_year, high_year):
        year_str = str(x)
        year_pair = (year_str, year_str)
        years.append(year_pair)

    month = forms.ChoiceField(choices=months)
    year = forms.ChoiceField(choices=years)

    def __init__(self, *args, **kwargs):
        super(SipDemographicReportForm, self).__init__(*args, **kwargs)
        current_year = datetime.now().year
        self.initial['year'] = str(current_year)


class SipCSFReportForm(forms.Form):
    current_year = datetime.now().year
    old_year = current_year - 20
    high_year = current_year + 2

    years = []
    for x in range(old_year, high_year):
        year_str = str(x)
        year_pair = (year_str, year_str)
        years.append(year_pair)

    quarter = forms.ChoiceField(choices=quarters)
    year = forms.ChoiceField(choices=years)

    def __init__(self, *args, **kwargs):
        super(SipCSFReportForm, self).__init__(*args, **kwargs)
        current_year = datetime.now().year
        self.initial['year'] = str(current_year)
        self.fields['year'].label = "Year (Start of Fiscal Year)"


class VolunteerReportForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(VolunteerReportForm, self).__init__(*args, **kwargs)


class VolunteerForm(forms.ModelForm):

    class Meta:
        model = Volunteer
        exclude = ('created', 'modified', 'user')


class VolunteerHoursForm(forms.ModelForm):
    volunteer_list = Contact.objects.filter(volunteer_check=1).order_by('last_name')
    contact = forms.ModelChoiceField(queryset=volunteer_list)

    class Meta:
        model = Volunteer
        exclude = ('created', 'modified', 'user')


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('document', )


class VaccineForm(forms.ModelForm):
    vaccination_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Vaccination Date', initial=timezone.now())

    class Meta:
        model = Vaccine
        exclude = ('created', 'modified', 'user', 'contact')
        widgets = {
            # "vaccination_date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(VaccineForm, self).__init__(*args, **kwargs)
        self.fields['vaccine'].label = "Type"
        self.fields['vaccination_date'].label = "Date"
        self.fields['vaccine_note'].label = "Notes"


class AssignmentForm(forms.ModelForm):
    # assignment_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Assignment Date', initial=timezone.now())

    class Meta:
        model = Assignment
        exclude = ('created', 'modified', 'user', 'assignment_date')
        widgets = {
            # "assignment_date": forms.DateInput(attrs={'type': 'date'})
        };


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


def filter_units(authorization_id): #remove any selections that would take instructor over allotted hours
    authorization = Authorization.objects.get(id=authorization_id)
    note_list = LessonNote.objects.filter(authorization_id=authorization_id)

    total_time = authorization.total_time
    minutes = total_time * 60
    total_time = minutes / 15

    total_units = 0
    for note in note_list:
        if note.billed_units:
            units = float(note.billed_units)
            total_units += units
    if total_units is None or len(str(total_units)) == 0:
        total_units = 0
    remaining = total_time - total_units

    choices_dictionary = {}
    for key, value in UNITS:
        if key <= remaining:
            choices_dictionary[key] = value

    return choices_dictionary
