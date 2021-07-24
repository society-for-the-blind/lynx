from django import forms
from django.utils.translation import gettext_lazy
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, SipPlan, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Volunteer, UNITS, Document

from datetime import datetime

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"),
          ('all', 'All Months'))

quarters = (("1", "Q1"), ("2", "Q2"), ("3", "Q3"), ("4", "Q4"))


class ContactForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))
    # user = forms.CharField(widget=forms.HiddenInput())

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['volunteer_check'].label = "Volunteer"


class IntakeForm(forms.ModelForm):
    intake_date = forms.CharField(widget=forms.DateInput(attrs={'aria-required': 'true'}))

    class Meta:

        model = Intake
        exclude = ('contact', 'created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(IntakeForm, self).__init__(*args, **kwargs)
        self.fields['intake_date'].label = "Intake Date (YYYY-MM-DD)"
        self.fields['eye_condition_date'].label = "Eye Condition Onset Date (YYYY-MM-DD)"
        self.fields['birth_date'].label = "Birthdate (YYYY-MM-DD)"
        self.fields['other_languages'].label = "Other Language(s)"
        self.fields['other_ethnicity'].label = "Ethnicity (if other)"
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
    # start_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    # end_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:

        model = Authorization
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['outside_agency'].label = "Payment Source"
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
    # date = forms.CharField(widget=forms.CharField(attrs={"onChange": 'checkDate(this)'}))

    class Meta:
        model = LessonNote
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(LessonNoteForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = "Lesson Note Date (YYYY-MM-DD)"


class SipNoteForm(forms.ModelForm):
    # currentYear = datetime.now().year
    # oldYear = 2000
    # highYear = currentYear + 2
    #
    # note_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(oldYear, highYear)))
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)

    class Meta:
        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id')
        super(SipNoteForm, self).__init__(*args, **kwargs)
        self.fields['sip_plan'].queryset = SipPlan.objects.filter(contact_id=contact_id)
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
        # self.fields['modesto'].label = "Modesto training site"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"
        self.fields['instructor'].label = "Instructor"
        self.fields['sip_plan'].label = "SIP Plan"


class SipNoteBulkForm(forms.ModelForm):
    # currentYear = datetime.now().year
    # oldYear = 2000
    # highYear = currentYear + 2
    #
    # note_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(oldYear, highYear)))
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)

    class Meta:
        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')

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


class SipPlanForm(forms.ModelForm):
    # currentYear = datetime.now().year
    # oldYear = 2015
    # highYear = currentYear + 1

    types = (("Retreat", "Retreat"), ("In-home", "In-home"), ("Support Group", "Support Group"),
              ("Training Seminar", "Training Seminar"), ("Workshop", "Workshop"))
    instructor = forms.CharField(required=False)
    plan_type = forms.ChoiceField(choices=types)
    start_date = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))

    class Meta:
        model = SipPlan
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(SipPlanForm, self).__init__(*args, **kwargs)
        self.fields['at_services'].label = "Assistive Technology Devices and Services"
        self.fields['independent_living'].label = "Independent Living and Adjustment Services"
        self.fields['orientation'].label = "Orientation & Mobility Training"
        self.fields['communications'].label = "Communication Skills Training"
        self.fields['dls'].label = "Daily Living Skills Training"
        self.fields['advocacy'].label = "Advocacy Training"
        self.fields['information'].label = "Information and Referral"
        self.fields['other_services'].label = "Other IL/A Services"
        self.fields['support_services'].label = "Supportive Services"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['living_plan_progress'].label = "Living Situation Outcome"
        self.fields['community_plan_progress'].label = "Home and Community Involvement Outcome"
        self.fields['at_outcomes'].label = "AT Goal Outcomes"
        self.fields['ila_outcomes'].label = "IL/A Service Goal Outcome"
        self.fields['start_date'].label = "Start Date"


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

