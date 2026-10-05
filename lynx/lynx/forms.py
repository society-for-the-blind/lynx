from http import client

from django       import forms
from django.utils import timezone
from datetime     import datetime, date
from django.db           import models    as ddm
from django.db.models    import functions as ddmf
from django.contrib.auth import models    as dca

# lm  = lynx model
from . import models  as lm
from .utils import kitchen_sink as lks

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

    # `plan_name` dropdown shows all plan names for the service event's pariticipants; service events and contacts have a many to many relationship but all participants for a service event share the same plan name and program name so just show the first participant's plan name and program name in the dropdown. The plan name is used to determine which plan the note will be saved into
    plan_name = forms.ChoiceField(
        choices=[],
        required=True,
        label='Plan Name',
    )

    note_date = forms.DateField(
        widget=forms.SelectDateWidget(years=list(range(2000, 2100))),
        required=True,
        label='Note Date',
    )
    event_length = forms.ChoiceField(
        choices=lks.DURATION_CHOICES,
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

    def _set_plan_type_choices(self, service_event, contact_id=None):

        note_choices = { 'in-home': [], 'group': [] }
        for pk, name in lm.OIBServiceDeliveryType.get_leaf_nodes():
            if int(pk) == 1:
                # in-home
                note_choices['in-home'].append((pk, name))
            else:
                # group
                note_choices['group'].append((pk, name))

        # Handle adding a new service event
        if service_event is None:
            if contact_id is not None:
                self.fields['plan_type'].choices = note_choices['in-home']
            else:
                self.fields['plan_type'].choices = note_choices['group']
            return

        # Handle editing an existing service event
        delivery_type_id = getattr(service_event, 'oib_service_delivery_type_id', None)
        self.fields['plan_type'].initial = delivery_type_id
        # If delivery type is in-home: allow all choices.
        # If delivery type is not in-home, enable all choices except in-home.
        if delivery_type_id != 1:
            plan_type_name = service_event.oib_service_delivery_type.oib_service_delivery_type
            self.fields['plan_type'].choices = note_choices['group']
        else:
            self.fields['plan_type'].choices = note_choices['in-home']
        return

    def _set_plan_choices_from_event(self, service_event, in_home_client_id):

        def get_current_grant_year_in_home_plans(contact_id):
            result = []
            # Get all joined OIBServiceEventContact records for client for
            # in-home service events.
            sec_in_home_qs = lm.OIBServiceEventContact.objects \
                .select_related('oib_plan','oib_service_event') \
                .filter(contact_id=contact_id, oib_service_event__oib_service_delivery_type_id=1) \
                .order_by('-oib_plan__oib_plan_name') \
                .distinct('oib_plan__oib_plan_name')

            for in_home_sec in sec_in_home_qs:
                plan_name = in_home_sec.oib_plan.oib_plan_name
                # Plan names are unique, constructed via the following formula:
                # "<month>/<day>/<year> - <service_delivery_type_name>"
                date_part, _delivery_type_part = plan_name.split(' - ', 1)
                try:
                    plan_date = datetime.strptime(date_part, '%m/%d/%Y').date()
                    # Filter plans to only those in the same grant year as the service event (a grant year runs from Oct 1 to Sep 30)
                    if grant_year_start <= plan_date <= grant_year_end:
                        result.append(plan_name)
                except ValueError:
                    # If the date part is not a valid date, skip this plan name
                    continue
            return [(plan_name, plan_name) for plan_name in result]

        # service_event==None && in_home_client_id       => new in-home event
        # service_event==None && in_home_client_id==None => new group event
        # service_event       && in_home_client_id==None => edit event (group or in-home)
        grant_year = lks.get_grant_year(service_event)
        grant_year_start = date(grant_year, 10, 1)
        grant_year_end = date(grant_year + 1, 9, 30)

        contact_id = None
        # Edit an existing service event
        if service_event:
            # If delivery type is not "in-home" (id != 1) disable the dropdown
            delivery_type_id = getattr(service_event, 'oib_service_delivery_type_id', None)
            plan_choices = []
            if delivery_type_id != 1:
                plan_name_qs = service_event.oibserviceeventcontact_set.select_related('oib_plan')
                plan_name = plan_name_qs.first().oib_plan.oib_plan_name
                plan_choices.append((plan_name, plan_name))
                self.fields['plan_name'].widget.attrs['disabled'] = 'disabled'
            else:
                contact_id = service_event.oibserviceeventcontact_set.select_related('contact').first().contact_id
                in_home_plan_choices = get_current_grant_year_in_home_plans(contact_id)
                new_in_home_plan_name = lks.construct_plan_name(
                    service_delivery_type_name="in-home", default=False
                )
                in_home_plan_choices.append((new_in_home_plan_name, 'Create new in-home plan'))
                plan_choices = in_home_plan_choices
            self.fields['plan_name'].choices = plan_choices
            self.fields['plan_name'].required = False
            return
            # If it's an in-home, prepare for listing all in-home plans for client.
            # Current policy is that only in-homes can have multiple plans in a
            # grant year, and each in-home event should only have one participant,
            # therefore to list all in-home plans for a service event, we can just
            # get the first participant.
            sec_to_get_in_home_plans = service_event.oibserviceeventcontact_set.select_related('contact').first()
            contact_id = sec_to_get_in_home_plans.contact_id

        if in_home_client_id is None:
            # TODO: This needs to go in the view under POST; service_delivery_type_name
            #       is known by then.
            # new_group_plan_name = lks.construct_plan_name(default=True, service_delivery_type_id=?)
            self.fields['plan_name'].choices = []
            self.fields['plan_name'].widget = forms.HiddenInput()
            self.fields['plan_name'].required = False
            return

        self.fields['plan_name'].required = True
        self.fields['plan_name'].widget = forms.Select()

        contact_id = in_home_client_id

        in_home_plan_choices = get_current_grant_year_in_home_plans(contact_id)
        new_in_home_plan_name = lks.construct_plan_name(
            service_delivery_type_name="in-home", default=False
        )
        in_home_plan_choices.append((new_in_home_plan_name, 'Create new in-home plan'))
        self.fields['plan_name'].choices = in_home_plan_choices

        # ensure field is enabled
        self.fields['plan_name'].widget.attrs.pop('disabled', None)

    def __init__(self, *args, user=None, service_event_id=None, in_home=False, in_home_client_id=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        service_event = None

        # import pdb; pdb.set_trace() 

        if service_event_id:
            try:
                service_event = lm.OIBServiceEvent.objects.get(id=service_event_id)
                self.fields['note_date'].initial = service_event.date
            except lm.OIBServiceEvent.DoesNotExist:
                service_event = None
        self._set_plan_choices_from_event(service_event, in_home_client_id)
        self._set_plan_type_choices(service_event, contact_id=in_home_client_id)
        # accept `user` so validation can allow admin override
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
