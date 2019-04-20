from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Contact, Address, Intake, Email, Phone, Medical, Referral, IntakeNote, EmergencyContact


# class IntakeFormContact(forms.Form):
    # first_name = forms.CharField(label='First Name', max_length=100)
    # initial = forms.CharField(label='Middle Initial', max_length=10, required=False)
    # last_name = forms.CharField(label='Last Name', max_length=100)
    # company = forms.CharField(label='Company', max_length=100, required=False)

class IntakeFormContact(forms.ModelForm):

    class Meta:

        model = Contact
        exclude = ('created', 'modified', 'user_id')

# class IntakeFormAddress(forms.Form):
#     address_one = forms.CharField(label='Address Line 1', max_length=100, required=False)
#     address_two = forms.CharField(label='Address Line 2', max_length=100, required=False)
#     apartment = forms.CharField(label='Suite or Apartment Number', max_length=100, required=False)
#     state = forms.ChoiceField(label='State', choices=STATES, initial='California', required=False)
#     zip = forms.CharField(label='Zip Code', max_length=100, required=False)
#     county = forms.ChoiceField(label='County', choices=COUNTIES, initial='Sacramento', required=False)
#     region = forms.ChoiceField(label='SIR Region', choices=REGIONS, required=False)
#     cross_street = forms.CharField(label='Major Cross Street', max_length=100, required=False)
#     phone_day = forms.CharField(label='Daytime Phone', max_length=100, required=False)
#     phone_night = forms.CharField(label='Evening Phone', max_length=100, required=False)
#     phone_other = forms.CharField(label='Other Phone', max_length=100, required=False)
#     no_mail = forms.CharField(label='Remove from Mailing List', max_length=100, required=False)


class IntakeFormAddress(forms.ModelForm):

    class Meta:

        model = Address
        exclude = ('created', 'modified', 'user_id', 'billing', 'contact_id')


# class IntakeFormOther(forms.Form):
#     gender = forms.ChoiceField(label='Gender', choices=GENDERS, required=False)
#     ethnicity = forms.ChoiceField(label='Ethnicity', choices=ETHNICITIES, required=False)
#     other_ethnicity = forms.CharField(label='Ethnicity if Other', max_length=100, required=False)
#     first_language = forms.CharField(label='First Language', max_length=100, required=False)
#     second_language = forms.CharField(label='Second Language', max_length=100, required=False)
#     birthdate = forms.CharField(label='Birth Date', max_length=100, required=False)
#     ssn = forms.CharField(label='Social Security (use ###-##-####)', max_length=15, required=False)
#     mailings = forms.ChoiceField(label='Medium for Mailings', choices=MAILINGS, required=False)


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


# class IntakeFormCriminal(forms.Form):
#     crime = forms.ChoiceField(label='Have you been convicted of a crime?', choices=TRINARY, initial='No', required=False)
#     crime_other = forms.CharField(label='Criminal Conviction if Other', max_length=100, required=False)
#     crime_info = forms.CharField(label='If yes, what and when did the convictions occur? '
#                                        'What county did this conviction occur in?', max_length=250, required=False)
#     parole = forms.ChoiceField(label='Are you on parole?', choices=TRINARY, initial='No', required=False)
#     parole_info = forms.CharField(label='Parole Information if Other', max_length=100, required=False)
#     criminal_history = forms.CharField(label='Is there any other information regarding your criminal history '
#                                              'that we should know about?', max_length=500, required=False)


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


# class IntakeFormEmergency(forms.Form):
#     emergency_name1 = forms.CharField(label='Emergency Contact Name', max_length=100, required=False)
#     emergency_relationship1 = forms.CharField(label='Relationship to Client', max_length=100, required=False)
#     emergency_phone1 = forms.CharField(label='Day Phone', max_length=100, required=False)
#     emergency_phone2 = forms.CharField(label='Evening Phone', max_length=100, required=False)
#     emergency_phone3 = forms.CharField(label='Other Phone', max_length=100, required=False)


class IntakeFormEmergency(forms.ModelForm):

    class Meta:

        model = EmergencyContact
        exclude = ('created', 'modified', 'user_id', 'contact_id')

# class IntakeFormMedical(forms.Form):
#     eye_condition = forms.CharField(label='Eye Condition', max_length=100, required=False)
#     eye_condition_other = forms.CharField(label='Eye Condition Other', max_length=100, required=False)
#     eye_condition_date = forms.CharField(label='Date of Diagnosis', max_length=100, required=False)
#     degree = forms.CharField(label='Degree of Eye Condition', max_length=100, required=False)
#     prognosis = forms.CharField(label='Prognosis', max_length=100, required=False)
#     performs_tasks = forms.CharField(label='Performs Tasks', max_length=100, required=False)
#     diabetes = forms.BooleanField(label="Diabetes", required=False)
#     dialysis = forms.BooleanField(label="Dialysis", required=False)
#     hearing_loss = forms.BooleanField(label="Hearing Loss", required=False)
#     mobility = forms.BooleanField(label="Mobility Impaired", required=False)
#     stroke = forms.BooleanField(label="Stroke", required=False)
#     seizure = forms.BooleanField(label="Seizure", required=False)
#     heart = forms.BooleanField(label="Heart Problems", required=False)
#     high_bp = forms.BooleanField(label="High BP", required=False)
#     neuropathy = forms.BooleanField(label="Neuropathy", required=False)
#     pain = forms.BooleanField(label="Pain", required=False)
#     asthma = forms.BooleanField(label="Asthma", required=False)
#     cancer = forms.BooleanField(label="Cancer", required=False)
#     substance_abuse = forms.BooleanField(label="Substance Abuse", required=False)
#     memory_loss = forms.BooleanField(label="Memory Loss", required=False)
#     learning_disability = forms.BooleanField(label="Learning Disability", required=False)
#     allergies = forms.CharField(label='Allergies', max_length=100, required=False)
#     mental_health = forms.CharField(label='Mental Health', max_length=100, required=False)
#     other_medical = forms.CharField(label='Other Medical', max_length=100, required=False)
#     medications = forms.CharField(label='Medications', max_length=250, required=False)


class IntakeFormMedical(forms.ModelForm):

    class Meta:

        model = Medical
        exclude = ('created', 'modified', 'user_id')


# class IntakeFormHistory(forms.Form):
#     referred_by = forms.CharField(label='Referred By', max_length=100, required=False)
#     veteran = forms.BooleanField(label="Veteran", required=False)
#     current_client = forms.CharField(label='Current Client', max_length=100, required=False)
#     current_client_other = forms.CharField(label='Current Client Other', max_length=100, required=False)
#     payment_source = forms.CharField(label='Payment Source', max_length=100, required=False)
#     payment_source_other = forms.CharField(label='Payment Source Other', max_length=100, required=False)
#     education = forms.CharField(label='Education', max_length=100, required=False)
#     living_arrangement = forms.CharField(label='Living Arrangement', max_length=100, required=False)
#     residence_type = forms.CharField(label='Residence Type', max_length=100, required=False)
#     work_history = forms.CharField(label='Work History', max_length=100, required=False)


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
