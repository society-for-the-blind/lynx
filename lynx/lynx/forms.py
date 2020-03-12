from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, Referral, IntakeNote, EmergencyContact, Authorization, \
    ProgressReport, LessonNote, SipNote

from datetime import datetime


class ContactForm(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')


class IntakeForm(forms.ModelForm):
    currentYear = datetime.now().year
    oldYear = datetime.now().year - 125
    if oldYear < 1900:
        oldYear = 1900

    intake_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(oldYear, currentYear)))
    eye_condition_date = forms.DateField(widget=forms.SelectDateWidget(empty_label="Nothing", years=range(oldYear, currentYear)))
    birth_date = forms.DateField(widget=forms.SelectDateWidget(years=range(oldYear, currentYear)))

    class Meta:

        model = Intake
        exclude = ('contact', 'created', 'modified', 'user')

    def __init__(self, *args, **kwargs):
        super(IntakeForm, self).__init__(*args, **kwargs)
        self.fields['other_languages'].label = "Other Language(s)"
        self.fields['other_ethnicity'].label = "Ethnicity (if other)"
        self.fields['crime'].label = "Have you been convicted of a crime?"
        self.fields['crime_info'].label = "If yes, what and when did the convictions occur? What county did this conviction occur in?"
        self.fields['crime_other'].label = "Criminal Conviction Information"
        self.fields['parole'].label = "Are you on parole?"
        self.fields['parole_info'].label = "Parole Information"
        self.fields['crime_history'].label = "Additional Criminal History"
        self.fields['musculoskeletal'].label = "Musculoskeletal Disorders"
        self.fields['alzheimers'].label = "Alzheimer’s Disease/Cognitive Impairment"
        self.fields['other_medical'].label = "Other Medical Information"
        self.fields['hobbies'].label = "Hobbies/Interests"


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
        exclude = ('created', 'modified', 'user', 'contact', 'active')


class PhoneForm(forms.ModelForm):

    class Meta:

        model = Phone
        exclude = ('created', 'modified', 'user', 'contact', 'active')


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
