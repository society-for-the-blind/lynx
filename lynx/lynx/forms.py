from django import forms
from django.utils.translation import gettext_lazy
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, SipPlan, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Volunteer

from datetime import datetime

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"))

quarters = (("1", "Q1"), ("2", "Q2"), ("3", "Q3"), ("4", "Q4"))


class ContactForm(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['volunteer_check'].label = "Volunteer"


class IntakeForm(forms.ModelForm):
    # currentYear = datetime.now().year
    # oldYear = currentYear - 125
    # highYear = currentYear + 2
    # if oldYear < 1900:
    #     oldYear = 1900

    # intake_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(1990, highYear)))
    # eye_condition_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(1920, highYear)))
    # birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(oldYear, currentYear)))

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

    class Meta:
        model = LessonNote
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(LessonNoteForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = "Lesson Note Date (YYYY-MM-DD)"

    def clean_total_time(self):
        data = self.cleaned_data.get('total_time')
        return data

    def clean_total_used(self):
        data = self.cleaned_data.get('total_used')
        return data

    def clean_billed_units(self):
        data = self.cleaned_data.get('billed_units')

        from .views import units_to_hours
        total_time = self.cleaned_data.get('total_time')
        total_used = self.cleaned_data.get('total_used')
        if total_used is None or len(total_used) == 0:
            total_used = 0

        note_hours = units_to_hours(int(data))
        total_hours = float(total_used) + note_hours

        if total_hours > float(total_time):
            raise ValidationError(
                _('Not enough time on the authorization'),
            )
        return data


class SipNoteForm(forms.ModelForm):
    note_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    client_list = Contact.objects.filter(sip_client=1).order_by('last_name')
    # client_list = Contact.objects.filter(active=1).filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list, required=False)

    currentYear = datetime.now().year
    oldYear = 2000
    highYear = currentYear + 2
    x = range(2000, highYear)
    years = []
    for n in x:
        print(n)

    class Meta:
        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact', 'modesto')

    def __init__(self, *args, **kwargs):
        super(SipNoteForm, self).__init__(*args, **kwargs)
        # self.fields['sip_plan'].queryset = SipPlan.objects.filter(contact_id=kwargs.get("contact_id"))

        self.fields['vision_screening'].label = "Vision screening/examination/low vision evaluation"
        self.fields['treatment'].label = "Surgical or therapeutic treatment"
        self.fields['at_devices'].label = "Provision of assistive technology devices and aids (non prescription optics)"
        self.fields['at_services'].label = "Provision of assistive technology services"
        self.fields['independent_living'].label = "Independent living and adjustment skills training"
        self.fields['orientation'].label = "Orientation and Mobility training"
        self.fields['communications'].label = "Communication skills"
        self.fields['dls'].label = "Daily Living Skills"
        self.fields['support'].label = "Support services"
        self.fields['advocacy'].label = "Advocacy training and support networks"
        self.fields['information'].label = "Information, referral, and community integration"
        self.fields['services'].label = "Other IL services"
        self.fields['in_home'].label = "In-home training"
        self.fields['seminar'].label = "Training Seminar"
        # self.fields['modesto'].label = "Modesto training site"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"
        self.fields['instructor'].label = "Instructor"
        self.fields['sip_plan'].label = "SIP Plan"

        self.fields['clients'].widget.attrs\
            .update({
                'aria-multiselectable': 'true',
                # 'class': 'input-calss_name'
            })


class SipPlanForm(forms.ModelForm):

    class Meta:
        model = SipPlan
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(SipPlanForm, self).__init__(*args, **kwargs)
        self.fields['at_services'].label = "Assistive Technology or Services"
        self.fields['independent_living'].label = "IL/A Services"
        self.fields['orientation'].label = "O&M Skills"
        self.fields['communications'].label = "Communication skills"
        self.fields['dls'].label = "Daily Living Skills"
        self.fields['advocacy'].label = "Advocacy training"
        self.fields['information'].label = "I&R (Information & Referral)"
        self.fields['other_services'].label = "Other services"
        self.fields['counseling'].label = "Adjustment Counseling"
        self.fields['living_plan_progress'].label = "Living Situation Outcomes"
        self.fields['community_plan_progress'].label = "Home and Community involvement Outcomes"
        self.fields['at_outcomes'].label = "AT Goal Outcomes"
        self.fields['ila_outcomes'].label = "IL/A Service Goal Outcomes"


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


class VolunteerForm(forms.ModelForm):

    class Meta:

        model = Volunteer
        exclude = ('created', 'modified', 'user')