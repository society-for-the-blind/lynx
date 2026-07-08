from django       import forms
from django.utils import timezone
from datetime     import datetime, date
from django.db           import models    as ddm
from django.db.models    import functions as ddmf
from django.contrib.auth import models    as dca

# lm  = lynx model
from . import models  as lm

months = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"), ("6", "June"),
          ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"), ("11", "November"), ("12", "December"),
          ('all', 'All Months'))

quarters = (("1", "Q1"), ("2", "Q2"), ("3", "Q3"), ("4", "Q4"))


class ContactForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))
    last_name  = forms.CharField(widget=forms.TextInput(attrs={'aria-required': 'true'}))

    programs = forms.ModelMultipleChoiceField(
        queryset = lm.Program.objects.all(),
        widget   = forms.CheckboxSelectMultiple,
        required = False,
        label    = "Programs"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        contact = self.instance
        # Try to get birth_date from Intake
        birth_date = None
        if contact.pk:
            intake = contact.intake_set.exclude(birth_date__isnull=True).order_by('-intake_date').first()
            if intake:
                birth_date = intake.birth_date
        # Compute age
        age = None
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        # Filter programs by age
        qs = lm.Program.objects.all()
        if age is not None:
            qs = qs.filter(
                ddm.Q(min_age=-1) | ddm.Q(min_age__lte=age),
                ddm.Q(max_age=-1) | ddm.Q(max_age__gte=age)
            )
        self.fields['programs'].queryset = qs

        # --- Set initial checked programs to active memberships ---
        if contact.pk:
            active_programs = lm.Program.objects.filter(
                contactprogram__contact=contact,
                contactprogram__end_date__isnull=True
            )
            self.initial['programs'] = list(active_programs.values_list('pk', flat=True))
            # This line ensures the field does not use instance's related objects
            self.fields['programs'].initial = list(active_programs.values_list('pk', flat=True))

    class Meta:
        model = lm.Contact
        fields = '__all__'

class IntakeForm(forms.ModelForm):
    intake_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Intake Date', initial=timezone.now())
    birth_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Birth Date', initial=timezone.now())
    eye_condition_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Onset date of eye condition', initial=timezone.now())
    hire_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Hire Date', initial=timezone.now())


    class Meta:
        model = lm.Intake
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
        self.fields['payment_source'].queryset = lm.Contact.objects.filter(payment_source=1).order_by(ddmf.Lower('last_name'))
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

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        contact = self.instance.contact if self.instance.pk else self.initial.get('contact')

        # Only check if birth_date is being changed
        if contact and birth_date:
            # Get the previous birth_date from the DB
            prev_intake = contact.intake_set.exclude(birth_date__isnull=True).order_by('-intake_date').first()
            prev_birth_date = prev_intake.birth_date if prev_intake else None
            if prev_birth_date and birth_date != prev_birth_date:
                invalid_programs = []
                for cp in contact.contactprogram_set.filter(end_date__isnull=True):
                    age = cp.start_date.year - birth_date.year - ((cp.start_date.month, cp.start_date.day) < (birth_date.month, birth_date.day))
                    min_age = cp.program.min_age
                    max_age = cp.program.max_age
                    if (min_age != -1 and age < min_age) or (max_age != -1 and age > max_age):
                        invalid_programs.append(cp.program.program)
                if invalid_programs and not self.data.get('confirm_birth_date_change'):
                    raise forms.ValidationError(
                        f"Changing birth date will make client ineligible for: {', '.join(invalid_programs)}. "
                        "Please confirm to proceed."
                    )
        return cleaned_data

class AddressForm(forms.ModelForm):

    class Meta:

        model = lm.Address
        exclude = ('created', 'modified', 'user', 'contact')

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['suite'].label = "Apt/Suite"


class EmergencyForm(forms.ModelForm):

    class Meta:

        model = lm.EmergencyContact
        exclude = ('created', 'modified', 'user', 'contact')


class EmailForm(forms.ModelForm):

    class Meta:

        model = lm.Email
        exclude = ('created', 'modified', 'user', 'contact', 'active', 'emergency_contact')


class PhoneForm(forms.ModelForm):

    class Meta:

        model = lm.Phone
        exclude = ('created', 'modified', 'user', 'contact', 'active', 'emergency_contact')


class IntakeNoteForm(forms.ModelForm):

    class Meta:

        model = lm.IntakeNote
        fields = ('note',)


class AuthorizationForm(forms.ModelForm):
    start_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Start Date', initial=timezone.now())
    end_date   = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='End Date', initial=timezone.now())

    class Meta:

        model = lm.Authorization
        exclude = ('created', 'modified', 'user', 'contact')
        widgets = {
            # "start_date": forms.DateInput(attrs={'type': 'date'}),
            # "end_date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['outside_agency'].queryset = lm.Contact.objects.filter(payment_source=1).order_by(ddmf.Lower('last_name'))
        self.fields['outside_agency'].label = "Payment Sources"
        self.fields['start_date'].label = "Start Date (YYYY-MM-DD)"
        self.fields['end_date'].label = "End Date (YYYY-MM-DD)"


class ProgressReportForm(forms.ModelForm):

    class Meta:

        model = lm.ProgressReport
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
    billed_units = forms.ChoiceField(choices=lm.UNITS, widget=forms.Select(attrs={"onChange": 'checkHours(this)'}))
    date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Lesson date', initial=timezone.now())

    class Meta:
        model = lm.LessonNote
        exclude = ('created', 'modified', 'user')
        widgets = {
            # "date": forms.DateInput(attrs={'type': 'date'})
        };

    def __init__(self, *args, **kwargs):
        super(LessonNoteForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = "Lesson Note Date (YYYY-MM-DD)"

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

class DocumentForm(forms.ModelForm):

    class Meta:
        model = lm.Document
        fields = ('document', )


class VaccineForm(forms.ModelForm):
    vaccination_date = forms.DateField( widget=forms.SelectDateWidget(years=list(range(1900, 2100))), label='Vaccination Date', initial=timezone.now())

    class Meta:
        model = lm.Vaccine
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
        model = lm.Assignment
        exclude = ('created', 'modified', 'user', 'assignment_date', 'assignment_status')
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


def filter_units(authorization_id):
    authorization = lm.Authorization.objects.get(id=authorization_id)
    note_list = lm.LessonNote.objects.filter(authorization_id=authorization_id)

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
    for key, value in lm.UNITS:
        if key <= remaining:
            choices_dictionary[key] = value

    return choices_dictionary

DURATION_CHOICES = [
    ("00:15:00", "15 minutes"),
    ("00:30:00", "30 minutes"),
    ("00:45:00", "45 minutes"),
    ("01:00:00", "1 hour"),
    ("01:15:00", "1 hour 15 minutes"),
    ("01:30:00", "1 hour 30 minutes"),
    ("01:45:00", "1 hour 45 minutes"),
    ("02:00:00", "2 hours"),
    ("02:15:00", "2 hours 15 minutes"),
    ("02:30:00", "2 hours 30 minutes"),
    ("02:45:00", "2 hours 45 minutes"),
    ("03:00:00", "3 hours"),
    ("03:15:00", "3 hours 15 minutes"),
    ("03:30:00", "3 hours 30 minutes"),
    ("03:45:00", "3 hours 45 minutes"),
    ("04:00:00", "4 hours"),
    ("04:15:00", "4 hours 15 minutes"),
    ("04:30:00", "4 hours 30 minutes"),
    ("04:45:00", "4 hours 45 minutes"),
    ("05:00:00", "5 hours"),
    ("05:15:00", "5 hours 15 minutes"),
    ("05:30:00", "5 hours 30 minutes"),
    ("05:45:00", "5 hours 45 minutes"),
    ("06:00:00", "6 hours"),
    ("06:15:00", "6 hours 15 minutes"),
    ("06:30:00", "6 hours 30 minutes"),
    ("06:45:00", "6 hours 45 minutes"),
    ("07:00:00", "7 hours"),
    ("07:15:00", "7 hours 15 minutes"),
    ("07:30:00", "7 hours 30 minutes"),
    ("07:45:00", "7 hours 45 minutes"),
    ("08:00:00", "8 hours"),
]

class OIBServiceMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.long_name

class OIBServiceEventForm(forms.Form):
    # A.k.a. service delivery type
    # The narrative is that the note will be saved into
    # the appropriate plan based on the date of the note
    # and service delivery type - but the twist is that
    # all plans are auto-generated on user query.
    #
    # Given that plans are hopelessly underspecified and
    # not even DOR knows what they want, we settled on
    #
    #    1 plan / year / client / service delivery type
    #
    plan_type = forms.ChoiceField(
        choices=lambda: lm.OIBServiceDeliveryType.get_leaf_nodes(),
        initial=1,
        required=True,
        label='Plan Type',
    )
    note_date = forms.DateField(
        widget=forms.SelectDateWidget(years=list(range(1900, 2100))),
        required=True,
        label='Note Date',
    )
    event_length = forms.ChoiceField(
        choices=DURATION_CHOICES,
        required=True,
        label='Event Length',
    )
    services = OIBServiceMultipleChoiceField(
        # NOTE 2025_08_24_1631
        #      The order of services is explicitly set in `__init__` below
        #      as this is what users have gotten used to.
        queryset=lm.OIBService.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Services",
    )
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 6,
                'cols': 80,
                'style': 'resize: both;'  # allow horizontal + vertical resize
            }
        ),
        required=True,
        label='Note',
    )

    def __init__(self, *args, user=None, **kwargs):
        # accept `user` so validation can allow admin override
        self.user = user
        super().__init__(*args, **kwargs)
        desired_order = [0,1,2,3,4,5,7,8,6]
        when_list = [ddm.When(id=pk, then=pos) for pos, pk in enumerate(desired_order)]
        qs = lm.OIBService.objects.annotate(
            ordering=ddm.Case(*when_list, default=9999, output_field=ddm.IntegerField())
        ).order_by('ordering', 'long_name')
        self.fields['services'].queryset = qs

        # compute current grant-year start (Oct 1 of the grant that contains today)
        today = timezone.localdate()
        if today.month >= 10:
            grant_start = date(today.year, 10, 1)
        else:
            grant_start = date(today.year - 1, 10, 1)

        # years to show: from grant_start.year up to current year (inclusive)
        years = list(range(grant_start.year, today.year + 1))

        # if an initial note_date is provided and its year is outside the above range
        # (editing an old event), include that year so the widget can render the existing value
        initial_note_date = None
        if 'initial' in kwargs and isinstance(kwargs['initial'], dict):
            initial_note_date = kwargs['initial'].get('note_date')
        if not initial_note_date and hasattr(self, 'initial'):
            initial_note_date = self.initial.get('note_date')
        if initial_note_date:
            try:
                y = initial_note_date.year
                if y not in years:
                    years.append(y)
                    years.sort()
            except Exception:
                pass

        # set the widget with the compact year list and default initial to today
        self.fields['note_date'].widget = forms.SelectDateWidget(years=years)
        # expose grant start and latest-allowed date to the client (ISO format)
        latest_allowed = today  # allow up to today (no future dates)
        widget_attrs = {
            'data-grant-start': grant_start.isoformat(),
            'data-latest-allowed': latest_allowed.isoformat(),
            'data-field-name': 'note_date',
        }
        # tell the client script we can override when the current user is staff
        if getattr(self, 'user', None) and getattr(self.user, 'is_staff', False):
            widget_attrs['data-admin-override-available'] = '1'
        else:
            widget_attrs['data-admin-override-available'] = '0'
        self.fields['note_date'].widget.attrs.update(widget_attrs)
        if not self.initial.get('note_date'):
            self.fields['note_date'].initial = today

    def clean_note_date(self):
        """
        Enforce note_date ∈ [current grant-year start (Oct 1), today].
        Allow preserving an existing initial date if present (editing old events).
        """
        note_date = self.cleaned_data.get('note_date')
        if not note_date:
            return note_date

        # allow preserving existing initial date when editing
        initial_note_date = self.initial.get('note_date')
        if initial_note_date and note_date == initial_note_date:
            return note_date

        # admin override bypass: staff users may set the hidden admin_override input
        admin_override_flag = (self.data.get('admin_override') in ('1', 'true', 'on'))
        if getattr(self, 'user', None) and getattr(self.user, 'is_staff', False) and admin_override_flag:
            return note_date

        today = timezone.localdate()
        if today.month >= 10:
            grant_start = date(today.year, 10, 1)
        else:
            grant_start = date(today.year - 1, 10, 1)

        latest_allowed = today  # explicitly disallow future dates

        if note_date < grant_start or note_date > latest_allowed:
            raise forms.ValidationError(
                f"Note date must be between {grant_start.isoformat()} and {latest_allowed.isoformat()} (no future dates)."
            )
        return note_date

# TODO DRY up - there is an (almost) exact dup of this class in `filters.py`
class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name}, {obj.first_name}"

class OIBServiceEventUserRoleForm(forms.Form):
    instructor = UserModelChoiceField(
        queryset=lm.User.objects.filter(is_active=True).order_by('last_name'),
        label='Instructor',
        empty_label="Select an instructor",
        required=True,
        widget=forms.Select(attrs={'class': 'instructor-select'}),
    )
    role = forms.ModelChoiceField(
        queryset=lm.OIBServiceEventInstructorRole.objects.all().order_by('oib_service_event_instructor_role'),
        label='Role',
        empty_label="Select a role",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        desired_index = 0
        qs = self.fields['role'].queryset
        try:
            role_obj = qs.order_by('pk')[desired_index]
        except (IndexError, TypeError):
            role_obj = qs.order_by('pk').first()
        if role_obj:
            self.fields['role'].initial = role_obj.pk

# TODO DRY up, again - I'm pretty sure this has been duplicated elsewhere
#      (I think in the Clients link there is a similar dropdown that uses the
#       same parameters.)
class ContactModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.last_name}, {obj.first_name}"

class OIBServiceEventContactForm(forms.Form):
    # Show only contacts that have an active membership in an OIB program.
    # If you want to include past memberships remove the end_date__isnull filter.
    client = ContactModelChoiceField(
        queryset=lm.Contact.active_oib_qs(),
        label='Client',
        empty_label="Select a client",
        required=True,
        widget=forms.Select(attrs={'class': 'client-select'}),
    )

class OIBServiceEventFilterForm(forms.Form):
    client = forms.CharField(required=False, label="Client name (keyword)")
    # program = forms.ModelChoiceField(
    #     queryset=lm.Program.objects.filter(is_oib=True).order_by('program'),
    #     required=False,
    #     label="Program"
    # )
    service_delivery_type = forms.ModelChoiceField(
        # exclude the ROOT
        queryset=lm.OIBServiceDeliveryType.objects.exclude(pk=0).order_by('oib_service_delivery_type'),
        required=False,
        label="Plan type"
    )
    instructor = UserModelChoiceField(
        queryset=dca.User.objects.filter(groups__name='SIP', is_active=True).order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name')),
        required=False,
        label="Instructor"
    )
    entered_by = UserModelChoiceField(
        queryset=dca.User.objects.filter(groups__name='SIP', is_active=True).order_by(ddmf.Lower('last_name'), ddmf.Lower('first_name')),
        required=False,
        label="Entered by"
    )
    start_date = forms.DateField(required=False, label="Start date")
    end_date = forms.DateField(required=False, label="End date")
    keyword = forms.CharField(required=False, label="Keyword in note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        years = list(range(2000, 2101))
        self.fields['start_date'].widget = forms.SelectDateWidget(years=years)
        self.fields['end_date'].widget = forms.SelectDateWidget(years=years)

class NumberOfServicesForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=list(range(1900, 2100))))
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=list(range(1900, 2100))))
    include_event_dates = forms.BooleanField(required=False)
