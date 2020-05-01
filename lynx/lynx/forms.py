from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, Referral, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote

from datetime import datetime

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"))


class ContactForm(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')


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
        # self.fields['crime_other'].label = "Criminal Conviction Information"
        # self.fields['parole'].label = "Are you on parole?"
        # self.fields['parole_info'].label = "Parole Information"
        # self.fields['crime_history'].label = "Additional Criminal History"
        self.fields['musculoskeletal'].label = "Musculoskeletal Disorders"
        self.fields['alzheimers'].label = "Alzheimer’s Disease/Cognitive Impairment"
        self.fields['medical_notes'].label = "Medical History"
        self.fields['hobbies'].label = "Hobbies/Interests"
        self.fields['high_bp'].label = "High BP"
        self.fields['geriatric'].label = "Other Major Geriatric Concerns"
        self.fields['degree'].label = "Degree of Vision Loss"
        self.fields['secondary_eye_condition'].label = "Notes"
        self.fields['heart'].label = "Cardiovascular Disease"
        self.fields['heart_notes'].label = "Cardiovascular Disease Notes"
        self.fields['dexterity'].label = "Use of Hands, Arms, and Fingers"
        self.fields['dexterity_notes'].label = "Use of Hands, Arms, and Fingers Notes"
        self.fields['migraine'].label = "Migraine Headache"


class AddressForm(forms.ModelForm):

    class Meta:

        model = Address
        exclude = ('created', 'modified', 'user', 'billing', 'contact')


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


class ProgressReportForm(forms.ModelForm):

    class Meta:

        model = ProgressReport
        exclude = ('created', 'modified', 'user', 'authorization')

    def __init__(self, *args, **kwargs):
        super(ProgressReportForm, self).__init__(*args, **kwargs)
        self.fields['client_behavior'].label = "Client Attendance and Behavior"
        self.fields['short_term_goals'].label = "Short Term Learning Goals"
        self.fields['short_term_goals_time'].label = "Estimated Time for Short Term Goals"
        self.fields['long_term_goals'].label = "Long Term Learning Goals"
        self.fields['long_term_goals_time'].label = "Estimated Time for Long Term Goals"


class LessonNoteForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:

        model = LessonNote
        exclude = ('created', 'modified', 'user', 'authorization')


class SipNoteForm(forms.ModelForm):
    note_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing"))

    class Meta:

        model = SipNote
        exclude = ('created', 'modified', 'user', 'contact')


class BillingReportForm(forms.Form):
    current_year = datetime.now().year
    old_year = current_year - 20
    high_year = current_year + 2

    years = []
    for x in range(old_year, high_year):
        year_str = str(x)
        year_pair = (year_str, year_str)
        years.append(year_pair)

    month = forms.ChoiceField(choices = months)
    year = forms.ChoiceField(choices = years)

    def __init__(self, *args, **kwargs):
        super(BillingReportForm, self).__init__(*args, **kwargs)
        current_year = datetime.now().year
        self.initial['year'] = str(current_year)
