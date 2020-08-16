from django import forms
from django.utils.translation import gettext_lazy

from .models import Contact, Address, Intake, Email, Phone, Referral, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote, Volunteer

from datetime import datetime

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"))


class ContactForm(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['volunteer_check'].label = "Volunteer"


class IntakeForm(forms.ModelForm):
    currentYear = datetime.now().year
    oldYear = currentYear - 125
    highYear = currentYear + 2
    if oldYear < 1900:
        oldYear = 1900

    intake_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(1990, highYear)))
    eye_condition_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(1920, highYear)))
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(oldYear, currentYear)))

    class Meta:

        model = Intake
        exclude = ('contact', 'created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(IntakeForm, self).__init__(*args, **kwargs)
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
        self.fields['secondary_eye_condition'].label = "Notes"
        self.fields['heart'].label = "Cardiovascular Disease"
        self.fields['heart_notes'].label = "Cardiovascular Disease Notes"
        self.fields['dexterity'].label = "Use of Hands, Arms, and Fingers"
        self.fields['dexterity_notes'].label = "Use of Hands, Arms, and Fingers Notes"
        self.fields['migraine'].label = "Migraine Headache"
        self.fields['memory_loss'].label = "Memory Loss/Tension"
        self.fields['memory_loss_notes'].label = "Memory Loss/Tension Notes"


class AddressForm(forms.ModelForm):

    class Meta:

        model = Address
        exclude = ('created', 'modified', 'user', 'billing', 'contact')

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
    start_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    end_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:

        model = Authorization
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['outside_agency'].label = "Payment Source"


class ProgressReportForm(forms.ModelForm):

    class Meta:

        model = ProgressReport
        exclude = ('created', 'modified', 'user', 'authorization')

    def __init__(self, *args, **kwargs):
        super(ProgressReportForm, self).__init__(*args, **kwargs)
        self.fields['instructor'].label = "Instructor(s)"
        self.fields['accomplishments'].label = "Client Accomplishments"
        self.fields['client_behavior'].label = "Client Attendance and Behavior"
        self.fields['short_term_goals'].label = "Remaining Short Term Objectives"
        self.fields['short_term_goals_time'].label = "Estimated number of Hours needed for completion of short term objectives"
        self.fields['long_term_goals'].label = "Remaining Long Term Objectives"
        self.fields['long_term_goals_time'].label = "Estimated number of Hours needed for completion of long term objectives"


class LessonNoteForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:

        model = LessonNote
        exclude = ('created', 'modified', 'user', 'authorization')


class SipNoteForm(forms.ModelForm):
    note_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))
    client_list = Contact.objects.filter(active=1).filter(sip_client=1).order_by('last_name')
    clients = forms.ModelMultipleChoiceField(queryset=client_list)

    currentYear = datetime.now().year
    oldYear = 2000
    highYear = currentYear + 2
    x = range(2000, highYear)
    years = []
    for n in x:
        print(n)

    class Meta:
        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(SipNoteForm, self).__init__(*args, **kwargs)
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
        self.fields['modesto'].label = "Modesto training site"
        self.fields['group'].label = "Support group(s)"
        self.fields['community'].label = "Community Integration"
        self.fields['class_hours'].label = "Class Length"


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

        month = forms.ChoiceField(choices=months)
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