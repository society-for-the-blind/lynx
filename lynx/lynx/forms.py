from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, Referral, IntakeNote, \
    EmergencyContact


class ContactForm(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user')


class IntakeForm(forms.ModelForm):

    class Meta:

        model = Intake
        exclude = ('created', 'modified', 'user_id', 'contact_id')


class IntakeFormAddress(forms.ModelForm):

    class Meta:

        model = Address
        exclude = ('created', 'modified', 'user', 'billing', 'contact_id')


class IntakeFormOther(forms.ModelForm):

    class Meta:

        model = Intake
        fields = ('gender', 'ethnicity', 'other_ethnicity', 'first_language', 'second_language', 'other_languages',
                  'birth_date', 'ssn', 'preferred_medium')
        labels = {
            'ssn': _('Social Security (use ###-##-####)'),
            'other_ethnicity': _('Ethnicity if Other'),
            'preferred_medium': _('Medium for Mailings'),
        }


class IntakeFormCriminal(forms.ModelForm):

    class Meta:

        model = Intake
        fields = ('crime', 'crime_other', 'crime_info', 'parole', 'parole_info', 'crime_history')
        labels = {
            'crime': _('Have you been convicted of a crime?'),
            'crime_info': _('If yes, what and when did the convictions occur? What county did this conviction '
                            'occur in?'),
            'crime_other': _('Criminal Conviction Information'),
            'parole': _('Are you on parole?'),
            'parole_info': _('Parole Information'),
            'crime_history': _('Additional Criminal History'),
        }


class IntakeFormEmergency(forms.ModelForm):

    class Meta:

        model = EmergencyContact
        exclude = ('created', 'modified', 'user_id', 'contact_id')


# class IntakeFormMedical(forms.ModelForm):
#
#     class Meta:
#
#         model = Medical
#         exclude = ('created', 'modified', 'user_id')


class IntakeFormHistory(forms.ModelForm):

    class Meta: #TODO: missing some fields

        model = Intake
        fields = ('veteran', 'education', 'living_arrangement', 'residence_type', 'work_history', 'training_goals',
                  'training_preferences', 'other')


class IntakeFormEmail(forms.ModelForm):

    class Meta:

        model = Email
        exclude = ('created', 'modified', 'user_id','contact_id')


class IntakeFormPhone(forms.ModelForm):

    class Meta:

        model = Phone
        exclude = ('created', 'modified', 'user_id', 'contact_id')


class IntakeNoteForm(forms.ModelForm):

    class Meta:

        model = IntakeNote
        fields = ('note',)


class IntakeForm(forms.ModelForm):

    class Meta:

        model = IntakeNote
        exclude = ('created', 'modified', 'user_id', 'contact_id')