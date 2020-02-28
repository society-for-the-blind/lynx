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
    other_languages = forms.CharField(label='Other Language(s)', widget=forms.TextInput())
    other_ethnicity = forms.CharField(label='Ethnicity (if other)', widget=forms.TextInput())
    crime = forms.CharField(label='Have you been convicted of a crime?', widget=forms.TextInput())
    crime_info = forms.CharField(label='If yes, what and when did the convictions occur? What county did this conviction occur in?', widget=forms.TextInput())
    crime_other = forms.CharField(label='Criminal Conviction Information', widget=forms.TextInput())
    parole = forms.CharField(label='Are you on parole?', widget=forms.TextInput())
    parole_info = forms.CharField(label='Parole Information', widget=forms.TextInput())
    crime_history = forms.CharField(label='Additional Criminal History', widget=forms.TextInput())
    musculoskeletal = forms.CharField(label='Musculoskeletal Disorders', widget=forms.TextInput())
    alzheimers = forms.CharField(label='Alzheimer’s Disease/Cognitive Impairment', widget=forms.TextInput())
    other_medical = forms.CharField(label='Other Medical Information', widget=forms.TextInput())



    class Meta:

        model = Intake
        exclude = ('contact', 'created', 'modified', 'user')


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
