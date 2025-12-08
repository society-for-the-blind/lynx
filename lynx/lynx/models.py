from django.db import models, connection
from django import forms
from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import User

from django.core import exceptions as exc
from django_pgviews import view as pg
from datetime import datetime, date
from simple_history.models import HistoricalRecords

from collections import OrderedDict

from . import kitchen_sink as lks

STATES = (("Alabama", "Alabama"), ("Alaska", "Alaska"), ("Arizona", "Arizona"), ("Arkansas", "Arkansas"),
          ("California", "California"), ("Colorado", "Colorado"), ("Connecticut", "Connecticut"),
          ("Delaware", "Delaware"), ("Florida", "Florida"), ("Georgia", "Georgia"), ("Hawaii", "Hawaii"),
          ("Idaho", "Idaho"), ("Illinois", "Illinois"), ("Indiana", "Indiana"), ("Iowa", "Iowa"),
          ("Kansas", "Kansas"), ("Kentucky", "Kentucky"), ("Louisiana", "Louisiana"), ("Maine", "Maine"),
          ("Maryland", "Maryland"), ("Massachusetts", "Massachusetts"), ("Michigan", "Michigan"),
          ("Minnesota", "Minnesota"), ("Mississippi", "Mississippi"), ("Missouri", "Missouri"),
          ("Montana", "Montana"), ("Nebraska", "Nebraska"), ("Nevada", "Nevada"), ("New Hampshire", "New Hampshire"),
          ("New Jersey", "New Jersey"), ("New Mexico", "New Mexico"), ("New York", "New York"),
          ("North Carolina", "North Carolina"), ("North Dakota", "North Dakota"), ("Ohio", "Ohio"),
          ("Oklahoma", "Oklahoma"), ("Oregon", "Oregon"), ("Pennsylvania", "Pennsylvania"),
          ("Rhode Island", "Rhode Island"), ("South Carolina", "South Carolina"), ("South Dakota", "South Dakota"),
          ("Tennessee", "Tennessee"), ("Texas", "Texas"), ("Utah", "Utah"), ("Vermont", "Vermont"),
          ("Virginia", "Virginia"), ("Washington", "Washington"), ("West Virginia", "West Virginia"),
          ("Wisconsin", "Wisconsin"), ("Wyoming", "Wyoming"))

COUNTIES = (("Alameda", "Alameda"), ("Alpine", "Alpine"), ("Amador", "Amador"), ("Butte", "Butte"),
          ("Colusa", "Colusa"), ("Calaveras", "Calaveras"), ("Contra Costa", "Contra Costa"),
          ("Del Norte", "Del Norte"), ("El Dorado", "El Dorado"), ("Fresno", "Fresno"), ("Glenn", "Glenn"),
          ("Humboldt", "Humboldt"), ("Imperial", "Imperial"), ("Inyo", "Inyo"), ("Kern", "Kern"),
          ("Kings", "Kings"), ("Klamath", "Klamath"), ("Lake", "Lake"), ("Lassen", "Lassen"),
          ("Los Angeles", "Los Angeles"), ("Madera", "Madera"), ("Marin", "Marin"), ("Mariposa", "Mariposa"),
          ("Mendocino", "Mendocino"), ("Merced", "Merced"), ("Modoc", "Modoc"), ("Mono", "Mono"),
          ("Monterey", "Monterey"), ("Napa", "Napa"), ("Nevada", "Nevada"), ("Orange", "Orange"),
          ("Placer", "Placer"), ("Plumas", "Plumas"), ("Riverside", "Riverside"), ("Sacramento", "Sacramento"),
          ("San Benito", "San Benito"), ("San Bernardino", "San Bernardino"), ("San Diego", "San Diego"),
          ("San Francisco", "San Francisco"), ("San Joaquin", "San Joaquin"), ("San Luis Obispo", "San Luis Obispo"),
          ("San Mateo", "San Mateo"), ("Santa Barbara", "Santa Barbara"), ("Santa Clara", "Santa Clara"),
          ("Santa Cruz", "Santa Cruz"), ("Shasta", "Shasta"), ("Sierra", "Sierra"), ("Siskiyou", "Siskiyou"),
          ("Solano", "Solano"), ("Sonoma", "Sonoma"), ("Stanislaus", "Stanislaus"), ("Sutter", "Sutter"),
          ("Tehama", "Tehama"), ("Trinity", "Trinity"), ("Tulare", "Tulare"), ("Tuolumne", "Tuolumne"),
          ("Ventura", "Ventura"), ("Yolo", "Yolo"), ("Yuba", "Yuba"), ("Other/None", "Other/None"))

REGIONS = (("Chico", "Chico"), ("Diablo", "Diablo"), ("Fresno", "Fresno"), ("Sacramento", "Sacramento"),
           ("Other", "Other"))

GENDERS = (("Female", "Female"), ("Male", "Male"), ("Non-Binary", "Non-Binary"),
           ("Gender Non-Conforming", "Gender Non-Conforming"), ("Other (in notes)", "Other (in notes)"),
           ("Prefer Not to Say", "Prefer Not to Say"), )

ETHNICITIES = (("American Indian or Alaska Native", "American Indian or Alaska Native"), ("Asian", "Asian"),
               ("Black or African American", "Black or African American"),
               ("Native Hawaiian or Pacific Islander", "Native Hawaiian or Pacific Islander"), ("White", "White"),
               ("Did not self identify Race", "Did not self identify Race"),
               ("Two or More Races", "Two or More Races"))

OTHER_ETHNICITIES = (("Hispanic or Latino", "Hispanic or Latino"),)

MAILINGS = (("N/A", "N/A"), ("Print", "Print"), ("Large Print", "Large Print"), ("Braille", "Braille"),
            ("E-Mail", "E-Mail"), ("Cassette", "Cassette"))

TRINARY = (('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other'))

# single source of truth for age groups: (min_age_or_None, max_age_or_None, label)
AGE_GROUP_BOUNDS = [
    (None, 17, "younger than 18"),
    (18, 24, "18-24"),
    (25, 34, "25-34"),
    (35, 44, "35-44"),
    (45, 54, "45-54"),
    (55, 64, "55-64"),
    (65, 74, "65-74"),
    (75, 84, "75-84"),
    (85, None, "85 and older"),
]
# choices for forms/filters (derived from bounds so they can't drift)
AGES = tuple((label, label) for (_min, _max, label) in AGE_GROUP_BOUNDS)

MONTHS = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"),
            ("5", "May"), ("6", "June"), ("7", "July"), ("8", "August"), ("9", "September"),
            ("10", "October"), ("11", "November"), ("12", "December"))

LANGUAGES = (("English", "English"), ("Armenian", "Armenian"), ("Arabic", "Arabic"), ("Bengali", "Bengali"),
             ("Cantonese", "Cantonese"), ("Czech", "Czech"), ("Danish", "Danish"), ("Dutch", "Dutch"),
             ("Finnish", "Finnish"), ("French", "French"), ("German", "German"), ("Greek", "Greek"),
             ("Hebrew", "Hebrew"), ("Hindi (urdu)", "Hindi (urdu)"), ("Hmong", "Hmong"), ("Hungarian", "Hungarian"),
             ("Italian", "Italian"), ("Japanese", "Japanese"), ("Korean", "Korean"), ("Lithuanian", "Lithuanian"),
             ("Malayalam", "Malayalam"), ("Mandarin", "Mandarin"), ("Mon-khmer (cambodian)", "Mon-khmer (cambodian)"),
             ("Norwegian", "Norwegian"), ("Panjabi", "Panjabi"), ("Persian", "Persian"), ("Polish", "Polish"),
             ("Portuguese", "Portuguese"), ("Russian", "Russian"),  ("Slovak", "Slovak"), ("Samoan", "Samoan"),
             ("Spanish", "Spanish"), ("Swahili", "Swahili"), ("Swedish", "Swedish"), ("Tagalog", "Tagalog"),
             ("Thai (laotian)", "Thai (laotian)"), ("Turkish", "Turkish"), ("Ukrainian", "Ukrainian"),
             ("Vietnamese", "Vietnamese"))

EDUCATION = (("None", "None"), ("Less than High School", "Less than High School"), ("GED", "GED"),
             ("High School", "High School"), ("Associates", "Associates"), ("Bachelors", "Bachelors"),
             ("Masters", "Masters"), ("Doctorate", "Doctorate"))

PRONOUNS = (("He/Him", "He/Him"), ("She/Her", "She/Her"), ("They/Them", "They/Them"), ("Ve/Ver", "Ve/Ver"),
            ("Xe/Xim", "Xe/Xim"), ("Ze/Hir", "Ze/Hir"), ("Other (in notes)", "Other (in notes)"))

UNITS = (("0", "0 Minutes"), ("1", "15 Minutes"), ("2", "30 Minutes"), ("3", "45 Minutes"), ("4", "1 Hour"),
         ("5", "1 Hour 15 Minutes"), ("6", "1 Hour 30 Minutes"), ("7", "1 Hour 45 Minutes"), ("8", "2 Hours"),
         ("9", "2 Hours 15 Minutes"), ("10", "2 Hours 30 Minutes"), ("11", "2 Hours 45 Minutes"), ("12", "3 Hours"),
         ("13", "3 Hours 15 Minutes"), ("14", "3 Hours 30 Minutes"), ("15", "3 Hours 45 Minutes"), ("16", "4 Hours"),
         ("17", "4 Hours 15 Minutes"), ("18", "4 Hours 30 Minutes"), ("19", "4 Hours 45 Minutes"), ("20", "5 Hours"),
         ("21", "5 Hours 15 Minutes"), ("22", "5 Hours 30 Minutes"), ("23", "5 Hours 45 Minutes"), ("24", "6 Hours"),
         ("25", "6 Hours 15 Minutes"), ("26", "6 Hours 30 Minutes"), ("27", "6 Hours 45 Minutes"), ("28", "7 Hours"),
         ("29", "7 Hours 15 Minutes"), ("30", "7 Hours 30 Minutes"), ("31", "7 Hours 45 Minutes"), ("32", "8 Hours"))

SIP_UNITS = ((.25, "15 Minutes"), (.5, "30 Minutes"), (.75, "45 Minutes"), (1, "1 Hour"), (1.25, "1 Hour 15 Minutes"),
         (1.5, "1 Hour 30 Minutes"), (1.75, "1 Hour 45 Minutes"), (2, "2 Hours"), (2.25, "2 Hours 15 Minutes"),
         (2.5, "2 Hours 30 Minutes"), (2.75, "2 Hours 45 Minutes"), (3, "3 Hours"), (3.25, "3 Hours 15 Minutes"),
         (3.5, "3 Hours 30 Minutes"), (3.75, "3 Hours 45 Minutes"), (4, "4 Hours"), (4.25, "4 Hours 15 Minutes"),
         (4.5, "4 Hours 30 Minutes"), (4.75, "4 Hours 45 Minutes"), (5, "5 Hours"), (5.25, "5 Hours 15 Minutes"),
         (5.5, "5 Hours 30 Minutes"), (5.75, "5 Hours 45 Minutes"), (6, "6 Hours"), (6.25, "6 Hours 15 Minutes"),
         (6.5, "6 Hours 30 Minutes"), (6.75, "6 Hours 45 Minutes"), (7, "7 Hours"), (7.25, "7 Hours 15 Minutes"),
         (7.5, "7 Hours 30 Minutes"), (7.75, "7 Hours 45 Minutes"), (8, "8 Hours"))

SALUTATIONS = (("Mr.", "Mr."), ("Mrs.", "Mrs."), ("Miss", "Miss"), ("Ms.", "Ms."), ("Dr.", "Dr."), ("Prof.", "Prof."),
               ("Rev.", "Rev."))


TASKS = (('Visually', 'Visually'), ('Non-Visually', 'Non-Visually'),
         ('Both Visually and Non-Visually', 'Both Visually and Non-Visually'))

CONDITIONS = (('Cataracts', 'Cataracts'), ('Diabetic Retinopathy', 'Diabetic Retinopathy'),
              ('Glaucoma', 'Glaucoma'), ('Macular Degeneration', 'Macular Degeneration'),
              ('Other causes of visual impairment', 'Other causes of visual impairment'))

# TODO 2025_09_14_1221 What does this do?
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

# NOTE/TODO Both this model and the UI implementation are a mess.
#       ---------------------------------------------------------------
# For example, a generic Contact can't even be added because there is only
# "Add New Client" under the Clients link which is an Intake form...
#
class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    salutation = models.CharField(max_length=25, choices=SALUTATIONS, blank=True, null=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    do_not_contact = models.BooleanField(blank=True, default=False)
    deceased = models.BooleanField(blank=True, default=False)
    remove_mailing = models.BooleanField(blank=True, default=False)
    active = models.BooleanField(blank=True, default=True)
    payment_source = models.BooleanField(blank=True, default=False)
    contact_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    programs = models.ManyToManyField(
        'Program',
        through='ContactProgram',
        related_name='contacts',
        blank=True,
    )

    @classmethod
    def active_oib_qs(cls):
        """Contacts active in an OIB program (currently active memberships)."""
        return cls.objects.filter(
            active=True,
            deceased=False,
            contactprogram__program__is_oib=True,
            contactprogram__end_date__isnull=True
        ).distinct().order_by('last_name', 'first_name')

    def maybe_birth_date(self):
        """
        Return the most-recent non-null intake.birth_date for this contact, or None.
        """
        intake = (
            self.intake_set
            .exclude(birth_date__isnull=True)
            .order_by('-intake_date')
            .first()
        )
        return intake.birth_date if intake else None

    def maybe_age_on(self, on_date):
        dob = self.maybe_birth_date()
        if not dob or not on_date:
            return None
        return on_date.year - dob.year - ((on_date.month, on_date.day) < (dob.month, dob.day))
    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.id})

    class Meta:
        ordering = ['last_name', 'first_name']

class Program(models.Model):
    program = models.CharField(max_length=64, unique=True)
    long_name = models.CharField(max_length=255)
    is_oib = models.BooleanField(default=False)
    min_age = models.SmallIntegerField(default=-1, help_text='-1 = no minimum age')
    max_age = models.SmallIntegerField(default=-1, help_text='-1 = no maximum age')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.program}"

    @classmethod
    def get_available_programs(cls):
        return cls.objects.all()

    # NOTE 2025_11_02_1505 Why is this under the Program model and not under Contact?
    #
    #      Because if it would be under Contact, the semantics would imply that we are
    #      looking for the OIB program of the client's current age, whereas we need to
    #      find the appropriate OIB program for arbitrary ages (e.g., at service event
    #      dates).
    @classmethod
    def get_age_appropriate_oib_program(cls, contact_age):
        """
        Return the appropriate OIB Program for a contact of a given age - no matter if
        contact is an OIB client or not.
        """
        oib_programs = cls.objects.filter(is_oib=True)
        qs = oib_programs.filter(
            models.Q(min_age__lte=contact_age) | models.Q(min_age=-1),
            models.Q(max_age__gte=contact_age) | models.Q(max_age=-1),
        )
        # OIB programs should be mutually exclusive by age, so there should be at most
        # one match - but wwho knows what gets misconfigured in the admin page or what
        # the DOR future brings.
        program = qs.first()
        return program

class ContactProgram(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    program = models.ForeignKey('Program', on_delete=models.PROTECT)

    # Client is ACTIVE in program if `start_date` is set and `end_date` is NULL;
    # if both set, client has aged out of program.
    #
    # NOTE 2025_09_14_1315 `start_date` has to be set. (If client is checked for a program, they had to
    #                      have started it at some point.)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=True, null=True)

    # Conservative: mark whether we were able to validate age at save time
    age_verified = models.BooleanField(default=True, help_text="False when no DOB available to validate against")


    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            # start <= end (if both present)
            models.CheckConstraint(
                name='cp_start_before_end',
                check=models.Q(end_date__isnull=True) | models.Q(start_date__isnull=True) | models.Q(start_date__lte=models.F('end_date')),
            ),
        ]
        indexes = [
            models.Index(fields=['contact', 'start_date', 'end_date']),
        ]

    @property
    def is_active(self):
        return self.start_date is not None and self.end_date is None

    def _latest_birth_date(self):
        Intake = apps.get_model('lynx', 'Intake')
        intake = (
            Intake.objects
            .filter(contact_id=self.contact_id)
            .exclude(birth_date__isnull=True)
            .order_by('-intake_date')
            .first()
        )
        return intake.birth_date if intake else None

    def clean(self):
        """
        Conservative age validation policy:
         - If DOB missing -> set age_verified=False and allow save.
         - If DOB present -> enforce program min/max_age (raise ValidationError on violation).
        Interpret Program min/max_age == -1 as unbounded.
        """
        # need both sides to validate
        if not (self.contact_id and self.program_id):
            return

        dob = self._latest_birth_date()
        if not dob:
            # cannot validate; mark unverified but do not raise
            self.age_verified = False
            return

        # compute age on start_date (or today if start_date not set)
        on_date = self.start_date or date.today()
        age = on_date.year - dob.year - ((on_date.month, on_date.day) < (dob.month, dob.day))

        min_age = self.program.min_age
        max_age = self.program.max_age

        # interpret -1 as no bound
        if min_age != -1 and age < min_age:
            raise exc.ValidationError(f"Client age {age} on {on_date} is below program minimum {min_age}.")
        if max_age != -1 and age > max_age:
            raise exc.ValidationError(f"Client age {age} on {on_date} is above program maximum {max_age}.")

        # passed validation
        self.age_verified = True

    def save(self, *args, **kwargs):
        # run model validation (won't raise for missing DOB; will raise for age violations)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_id} -> {self.program.program}"

class Email (models.Model):
    EMAIL_TYPES = (("Work", "Work"), ("Personal", "Personal"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, null=True, blank=True)
    emergency_contact = models.ForeignKey('EmergencyContact', on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    email_type = models.CharField(max_length=25, choices=EMAIL_TYPES, blank=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contact_emails',
        null=True,
        blank=True,
        on_delete=models.SET(get_sentinel_user)
    )
    history = HistoricalRecords()

    def get_absolute_url(self):
        # NOTE Why check `self.contact`? See note in class `Phone` below.
        if self.contact:
            return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})
        else:
            return reverse('lynx:contact_show', kwargs={'pk': self.emergency_contact.contact_id})

    def __str__(self):
        return self.email


class Phone (models.Model):
    PHONE_TYPES = (("Work", "Work"), ("Home", "Home"), ("Cell", "Cell"), ("Evening", "Evening"), ("Day", "Day"),
                   ("Fax", "Fax"), ("Other", "Other"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, null=True, blank=True)
    emergency_contact = models.ForeignKey('EmergencyContact', on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    phone_type = models.CharField(max_length=25, choices=PHONE_TYPES, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        # NOTE Why check `self.contact`? {{-
        #
        #      On the  client page,  when editing the  phone number
        #      of  an  emergency contact,  then  there  will be  no
        #      `contact` property in self  for some reason, but the
        #      `lynx_emergencycontact`  table  has  a  `contact_id`
        #      column so it can be used to go back.
        # }}-
        if self.contact:
            return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})
        else:
            return reverse('lynx:contact_show', kwargs={'pk': self.emergency_contact.contact_id})

    def __str__(self):
        return self.phone


# Addresses for Contacts.
class Address(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, null=True, blank=True)
    address_one = models.CharField(max_length=150, blank=True, null=True)
    address_two = models.CharField(max_length=150, blank=True, null=True)
    suite = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=75, blank=True, null=True)
    state = models.CharField(max_length=25, choices=STATES, default='California', blank=True, null=True)
    zip_code = models.CharField(max_length=15, blank=True, null=True)
    county = models.CharField(max_length=150, choices=COUNTIES, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(max_length=150, blank=True, null=True)
    cross_streets = models.CharField(max_length=150, blank=True, null=True)
    bad_address = models.BooleanField(blank=True, default=False)
    # billing = models.BooleanField(blank=True, default=False)  # Only applies to employees
    preferred_medium = models.CharField(max_length=150, blank=True, choices=MAILINGS, null=True)
    address_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Addresses'

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})


# Intake questionnaire
class Intake(models.Model):
    INCOMES = (("<$12,500", "<$12,500"), ("$12,500-$25,000", "$12,500-$25,000"), ("$25,001-$50,000", "$25,001-$50,000"),
               ("$50,001-$75,000", "$50,001-$75,000"), ("$75,001-$100,000", "$75,001-$100,000"),
               ("$100,001-$125,000", "$100,001-$125,000"), ("$125,001-$1150,000", "$125,001-$150,000"),
               (">$150,000", ">$150,000"))

    LIVING = (("Live Alone", "Live Alone"), ("Live With Spouse or Family", "Live With Spouse or Family"),
              ("Live With Other", "Live With Other"), ("Homeless", "Homeless"))

    RESIDENCE = (("Private Residence", "Private Residence"),
                 ("Assisted Living Facility", "Assisted Living Facility"), ("Nursing Home", "Nursing Home"),
                 ("Senior Independent Living", "Senior Independent Living"), ("Homeless", "Homeless"))

    PROGNOSIS = (("Stable", "Stable"), ("Diminishing", "Diminishing"))

    DEGREE = (("Totally Blind", "Totally Blind"),
              ("Legally Blind", "Legally Blind"),
              ("Severe Vision Impairment", "Severe Vision Impairment"))

    REFERER = (("DOR", "DOR"), ("Alta", "Alta"), ("Veterans Administration", "Veterans Administration"),
               ("Family or Friend", "Family or Friend"), ("Senior Program", "Senior Program"),
               ("Assisted Living Facility", "Assisted Living Facility"), ("Nursing Home", "Nursing Home"),
               ("Independent Living Center", "Independent Living Center"), ("Self-Referral", "Self-Referral"),
               ("Physician/ Medical Provider", "Physician/ Medical Provider"),
               ("Eye Care Provider", "Eye Care Provider"), ("Other", "Other"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_date = models.DateField(default=date.today)
    intake_type = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, choices=GENDERS, null=True)
    pronouns = models.CharField(max_length=150, blank=True, choices=PRONOUNS, null=True)
    birth_date = models.DateField(blank=True, null=True)
    ethnicity = models.CharField(max_length=50, blank=True, choices=ETHNICITIES, null=True)
    other_ethnicity = models.CharField(max_length=50, blank=True, choices=OTHER_ETHNICITIES, null=True)
    income = models.CharField(max_length=25, choices=INCOMES, blank=True, null=True)
    first_language = models.CharField(max_length=50, blank=True, choices=LANGUAGES, null=True)
    second_language = models.CharField(max_length=50, blank=True, choices=LANGUAGES, null=True)
    other_languages = models.CharField(max_length=150, blank=True, null=True)
    education = models.CharField(max_length=150, blank=True, choices=EDUCATION, null=True)
    living_arrangement = models.CharField(max_length=150, blank=True, choices=LIVING, null=True)
    residence_type = models.CharField(max_length=150, blank=True, choices=RESIDENCE, null=True)
    performs_tasks = models.CharField(max_length=150, blank=True, choices=TASKS, null=True)
    notes = models.TextField(blank=True, null=True)
    work_history = models.TextField(blank=True, null=True)
    veteran = models.CharField(max_length=25, blank=True, null=True, choices=TRINARY)
    member_name = models.CharField(max_length=250, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True, default=True)
    crime = models.CharField(max_length=25, blank=True, null=True, choices=TRINARY)
    crime_info = models.TextField(blank=True, null=True)
    crime_other = models.CharField(max_length=250, blank=True, null=True)
    parole = models.BooleanField(blank=True, default=False)
    parole_info = models.CharField(max_length=250, blank=True, null=True)
    crime_history = models.TextField(blank=True, null=True)
    previous_training = models.TextField(blank=True, null=True)
    training_goals = models.TextField(blank=True, null=True)
    training_preferences = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    eye_condition = models.CharField(max_length=250, blank=True, null=True, choices=CONDITIONS)
    secondary_eye_condition = models.CharField(max_length=400, blank=True, null=True)
    eye_condition_date = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=250, blank=True, choices=DEGREE, null=True)
    prognosis = models.CharField(max_length=250, blank=True, choices=PROGNOSIS, null=True)
    referred_by = models.CharField(max_length=250, blank=True, choices=REFERER, null=True)
    payment_source = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='intake_outside_agent'
    )
    diabetes = models.BooleanField(blank=True, default=False)
    diabetes_notes = models.CharField(max_length=255, blank=True, null=True)
    dialysis = models.BooleanField(blank=True, default=False)
    dialysis_notes = models.CharField(max_length=255, blank=True, null=True)
    hearing_loss = models.BooleanField(blank=True, default=False)
    hearing_loss_notes = models.CharField(max_length=255, blank=True, null=True)
    mobility = models.BooleanField(blank=True, default=False)
    mobility_notes = models.CharField(max_length=255, blank=True, null=True)
    stroke = models.BooleanField(blank=True, default=False)
    stroke_notes = models.CharField(max_length=255, blank=True, null=True)
    seizure = models.BooleanField(blank=True, default=False)
    seizure_notes = models.CharField(max_length=255, blank=True, null=True)
    heart = models.BooleanField(blank=True, default=False)
    heart_notes = models.CharField(max_length=255, blank=True, null=True)
    arthritis = models.BooleanField(blank=True, default=False)
    arthritis_notes = models.CharField(max_length=255, blank=True, null=True)
    high_bp = models.BooleanField(blank=True, default=False)
    high_bp_notes = models.CharField(max_length=255, blank=True, null=True)
    neuropathy = models.BooleanField(blank=True, default=False)
    neuropathy_notes = models.CharField(max_length=255, blank=True, null=True)
    dexterity = models.BooleanField(blank=True, default=False)
    dexterity_notes = models.CharField(max_length=255, blank=True, null=True)
    migraine = models.BooleanField(blank=True, default=False)
    migraine_notes = models.CharField(max_length=255, blank=True, null=True)
    pain = models.BooleanField(blank=True, default=False)
    pain_notes = models.CharField(max_length=255, blank=True, null=True)
    asthma = models.BooleanField(blank=True, default=False)
    asthma_notes = models.CharField(max_length=255, blank=True, null=True)
    cancer = models.BooleanField(blank=True, default=False)
    cancer_notes = models.CharField(max_length=255, blank=True, null=True)
    musculoskeletal = models.BooleanField(blank=True, default=False)
    musculoskeletal_notes = models.CharField(max_length=255, blank=True, null=True)
    alzheimers = models.BooleanField(blank=True, default=False)
    alzheimers_notes = models.CharField(max_length=255, blank=True, null=True)
    geriatric = models.BooleanField(blank=True, default=False)
    geriatric_notes = models.CharField(max_length=255, blank=True, null=True)
    allergies = models.CharField(max_length=250, blank=True, null=True)
    mental_health = models.CharField(max_length=250, blank=True, null=True)
    substance_abuse = models.BooleanField(blank=True, default=False)
    substance_abuse_notes = models.CharField(max_length=255, blank=True, null=True)
    memory_loss = models.BooleanField(blank=True, default=False)
    memory_loss_notes = models.CharField(max_length=255, blank=True, null=True)
    learning_disability = models.BooleanField(blank=True, default=False)
    learning_disability_notes = models.CharField(max_length=255, blank=True, null=True)
    communication = models.BooleanField(blank=True, default=False)
    communication_notes = models.CharField(max_length=255, blank=True, null=True)
    other_medical = models.CharField(max_length=250, blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    employment_goals = models.TextField(blank=True, null=True)
    hired = models.CharField(max_length=25, blank=True, null=True, choices=TRINARY)
    employer = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    history = HistoricalRecords()
    updated = models.DateTimeField(auto_now=True, null=True)

    def _compute_age_on(self, on_date):
        if not self.birth_date:
            return None
        on_date = on_date or date.today()
        age = on_date.year - self.birth_date.year - (
            (on_date.month, on_date.day) < (self.birth_date.month, self.birth_date.day)
        )
        return age

    def _age_group_label_for_age(self, age):
        if age is None:
            return None
        for min_a, max_a, label in AGE_GROUP_BOUNDS:
            if min_a is None and max_a is not None:
                if age <= max_a:
                    return label
            elif max_a is None and min_a is not None:
                if age >= min_a:
                    return label
            else:
                if min_a <= age <= max_a:
                    return label
        return None

    def get_absolute_url(self):
        # keep behavior consistent with other models: go to the contact's page
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})

    @property
    def age_group(self):
        on_date = date.today()
        age = self._compute_age_on(on_date)
        return self._age_group_label_for_age(age)

    def __str__(self):
        return '%s Intake' % (self.contact_id,)


class IntakeNote(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    note_type = models.CharField(max_length=250, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})


# Addresses for Contacts.
class EmergencyContact(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    emergency_notes = models.TextField(blank=True, null=True)
    relationship = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})


class Authorization(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    outside_agency = models.ForeignKey(
        'Contact',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='outside_agent'
    )
    intake_service_area = models.ForeignKey('IntakeServiceArea', on_delete=models.CASCADE)
    authorization_number = models.CharField(max_length=150, blank=True, null=True)
    authorization_type = models.CharField(
        max_length=25,
        choices=(("Hours", "Hours"), ("Classes", "Classes")),
        blank=True,
        null=True
    )
    start_date = models.DateField(blank=True, null=True, default=date.today)
    end_date = models.DateField(blank=True, null=True, default=date.today)
    total_time = models.CharField(max_length=150, blank=True, null=True)
    billing_rate = models.CharField(max_length=150, blank=True, null=True)
    # outside_agency = models.ForeignKey('OutsideAgency', on_delete=models.CASCADE)
    student_plan = models.CharField(max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:authorization_detail', kwargs={'pk': self.id})


class OutsideAgency(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    agency = models.CharField(max_length=150, blank=True, null=True)
    contact_name = models.CharField(max_length=150, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = 'Outside Agencies'

    def __str__(self):
        return '%s - %s' % (self.contact_name, self.agency)


class IntakeServiceArea(models.Model):
    agency = models.CharField(max_length=150, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def __str__(self):
        return self.agency


class ProgressReport(models.Model):
    month = models.CharField(max_length=25, choices=MONTHS, blank=True, null=True)
    year = models.CharField(max_length=25, blank=True, null=True)
    authorization = models.ForeignKey('Authorization', on_delete=models.CASCADE)
    # TODO Remove as this is superfluous - there is already a ForeignKey to User.
    instructor = models.CharField(max_length=150, blank=True, null=True)
    accomplishments = models.TextField(blank=True, null=True)
    short_term_goals = models.TextField(blank=True, null=True)
    short_term_goals_time = models.CharField(max_length=150, blank=True, null=True)
    long_term_goals = models.TextField(blank=True, null=True)
    long_term_goals_time = models.CharField(max_length=150, blank=True, null=True)
    client_behavior = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:authorization_detail', kwargs={'pk': self.authorization_id})


class LessonNote(models.Model):
    authorization = models.ForeignKey('Authorization', on_delete=models.CASCADE, related_name='lesson')
    date = models.DateField(default=date.today, null=True)
    attendance = models.CharField(
        max_length=150,
        blank=True,
        choices=(
            ('Present', 'Present'),
            ('Absent', 'Absent'),
            ('Other', 'Other')
        ),
        null=True,
        default='Present'
    )
    instructional_units = models.CharField(max_length=15, blank=True, null=True)
    billed_units = models.CharField(max_length=50, blank=True, choices=UNITS, null=True)
    students_no = models.CharField(max_length=15, blank=True, null=True)
    successes = models.TextField(null=True, blank=True)
    obstacles = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:authorization_detail', kwargs={'pk': self.authorization_id})


class ContactInfoView(pg.View):
    sql = f"""
        SELECT c.id,
               concat(last_name, ', ', first_name) AS full_name,
               first_name,
               last_name,
               a.county,
               a.zip_code,
               REPLACE(REPLACE(REPLACE(REPLACE(p.phone, ' ', ''), '-', ''), ')', ''), '(', '') as phone,
               e.email,
               i.intake_date,
               -- compute age_group from the most recent intake.birth_date and CURRENT_DATE
               { lks.age_group_case_sql() } as age_group,
               a.address_one,
               a.address_two,
               a.suite,
               a.city,
               a.state,
               a.bad_address,
               c.do_not_contact,
               c.deceased,
               c.remove_mailing,
               a.region,
               phone as full_phone,
               c.active,
               array_to_string(array_agg(pr.program), ',') as programs
        FROM lynx_contact AS c
        LEFT JOIN LATERAL (
            SELECT ii.intake_date, ii.birth_date
            FROM lynx_intake ii
            WHERE ii.contact_id = c.id AND ii.birth_date IS NOT NULL
            ORDER BY ii.intake_date DESC NULLS LAST
            LIMIT 1
        ) i ON TRUE
        LEFT JOIN lynx_address AS a ON a.contact_id = c.id
        LEFT JOIN lynx_phone  AS p ON p.contact_id = c.id
        LEFT JOIN lynx_email AS e ON e.contact_id = c.id
        LEFT JOIN lynx_contactprogram cp ON cp.contact_id = c.id
        LEFT JOIN lynx_program pr ON cp.program_id = pr.id
        GROUP BY c.id, a.county, a.zip_code, p.phone, e.email, i.intake_date, i.birth_date,
                 a.address_one, a.address_two, a.suite, a.city, a.state, a.bad_address,
                 c.do_not_contact, c.deceased, c.remove_mailing, a.region, phone, c.active
    """

    full_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    intake_date = models.DateField(blank=True, null=True)
    age_group = models.CharField(max_length=255, null=True)
    address_one = models.CharField(max_length=255, null=True)
    address_two = models.CharField(max_length=255, null=True)
    suite = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    bad_address = models.BooleanField(blank=True, default=False)
    do_not_contact = models.BooleanField(blank=True, default=False)
    deceased = models.BooleanField(blank=True, default=False)
    remove_mailing = models.BooleanField(blank=True, default=False)
    active = models.BooleanField(blank=True, default=False)
    region = models.CharField(max_length=255, null=True)
    full_phone = models.CharField(max_length=255, null=True)
    programs = models.CharField(max_length=255, null=True)
    history = HistoricalRecords()

    class Meta:
        app_label = 'lynx'
        db_table = 'lynx_contactinfoview'
        managed = False


class Document(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()


class Vaccine(models.Model):
    VACCINES = (("P or M Dose 2", "P or M Dose 2"), ("J&J Single", "J&J Single"), ("Booster", "Booster"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    vaccine = models.CharField(max_length=25, blank=True, null=True, choices=VACCINES)
    vaccination_date = models.DateField(blank=True, null=True)
    vaccine_note = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

class AssignmentStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AssignmentPriority(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Assignment(models.Model):
    program = models.ForeignKey(
        'Program',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='assignments',
        default=1
    )

    priority = models.ForeignKey(
        AssignmentPriority,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='assignments',
        default=1
    )

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    # TODO/QUESTION: Why is there both a `user` and an `instructor` field?
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructors')
    assignment_date = models.DateField(auto_now_add=True, null=True)
    note = models.TextField(blank=True, null=True)

    assignment_status = models.ForeignKey(
        AssignmentStatus,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name='assignments',
        default=1
    )

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('lynx:assignment', kwargs={'pk': self.contact_id})

# === OIB RE-DESIGN =========================================================

# TODO 2025_09_28_1759 OIB Quarterly Report reminder with OIBProgram model gone
#                      ========================================================
#      There is going to be *one* SIP plan per client - and "SIP" here means the
#      department and not the OIB program. If a client ages into the OIB program
#      "SIP" from ILP, then they would count into both programs for that year. 
#
#      TODO-TODO Make sure.

# NOTE "service delivery type" === "plan type"
#      ----------------------------------------------------
#      On the front-end, this is called  "plan  type",  for
#      historical and  beurocratic  reasons.  Beaurocratic:
#      DOR wants lots of plans, and  having  one  plan  per
#      year per client per service  delivery  type  is  the
#      sweet spot. Historical: the original  implementation
#      is flawed, and every user now  thinks  of  these  as
#      "plan types". Damage done.
class OIBServiceDeliveryType(models.Model):
    parent_id = models.IntegerField(null=True, blank=True)
    oib_service_delivery_type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    # Show only the SDTs that are not categories themselves
    # (i.e. the leaf nodes of the hierarchy tree)
    #
    # TODO This doesn't really belong here as it is  not  a
    #      class method, but a simple function defined on a
    #      class, but not sure where to put it.
    def get_leaf_nodes():
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE cte AS (
                    SELECT t.id, t.parent_id, t.oib_service_delivery_type
                    FROM lynx_oibservicedeliverytype t
                    WHERE t.parent_id IS NULL
                    UNION ALL
                    SELECT t2.id, t2.parent_id, t2.oib_service_delivery_type
                    FROM lynx_oibservicedeliverytype t2
                    INNER JOIN cte ON t2.parent_id = cte.id
                )
                SELECT t3.id, t3.oib_service_delivery_type
                FROM lynx_oibservicedeliverytype t3
                WHERE t3.id NOT IN (SELECT parent_id FROM lynx_oibservicedeliverytype WHERE parent_id IS NOT NULL);
            """)
            rows = cursor.fetchall()
        # return choices: (id, label)
        return [(row[0], row[1]) for row in rows]

    def __str__(self):
        return self.oib_service_delivery_type

class OIBService(models.Model):
    oib_service = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.oib_service

class OIBServiceEvent(models.Model):
    # NOTE-1 See "0109_add_oibserviceeventcontact.py" for
    #        the diff between `organizer` and `OIBServiceEventContact.oib_program`
    # NOTE-2 The default OIB program is "SIP". 
    #      (This  is  may  not  even  be  necessary  and  I  am
    #      overthinking  it,   because   the   SIP   department
    #      organizes the events for all  OIB  programs,  so  it
    #      would  be  more   fitting   to   have   this   named
    #      `organizing_department`. In which case,  this  field
    #      is  just  plain  wrong.  Case  in  point,  I   think
    #      CareersPlus is its own department, for example.)
    #

    # NOTE This is the "plan" in the front-end.
    oib_service_delivery_type = models.ForeignKey(OIBServiceDeliveryType, on_delete=models.PROTECT)

    date = models.DateField(blank=True, default=date.today)
    # start_time = models.TimeField(blank=True, default="00:00:00")
    # end_time = models.TimeField(blank=True, default="00:00:00")
    length = models.DurationField(blank=True, default="00:00:00")
    note = models.TextField(blank=True, default="")
    entered_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="entered_service_events")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    # many-to-many relationships
    contacts = models.ManyToManyField(Contact,    through='OIBServiceEventContact',    through_fields=('oib_service_event', 'contact'))
    instructors = models.ManyToManyField(User,    through='OIBServiceEventInstructor', through_fields=('oib_service_event', 'instructor'))
    services = models.ManyToManyField(OIBService, through='OIBServiceEventOIBService', through_fields=('oib_service_event', 'oib_service'))

    def __str__(self):
        return f"{self.date} {self.oib_service_delivery_type} {self.date}"

    def get_grant_year(self):
        """
        Compute the Oct-Sep fiscal year for this event's date.
        """
        if self.date.month >= 10:
            return self.date.year
        else:
            return self.date.year - 1

    def get_plan_name(self, grant_year, program, servide_delivery_type_name):
        return f"{program or ''} 10/1/{grant_year} - {servide_delivery_type_name or ''}"

    def collect_service_names(self):
        service_names = set()
        for svc in self.services.all():
            name = getattr(svc, 'long_name', None) or getattr(svc, 'oib_service', None)
            if name:
                service_names.add(name)
        return service_names

    # TODO 2025_10_02_1540 Evaluate if these can be deleted once views.oib_plan_(show|edit) are refactored
    @classmethod
    def for_client(cls, contact_id):
        """
        Base queryset for a contact with useful joins for repeated use.
        """
        return cls.objects.filter(contacts__id=contact_id) \
                   .select_related('oib_service_delivery_type') \
                   .prefetch_related('services')

    @classmethod
    def with_grant_year_annotation(cls, qs=None):
        """
        Annotate queryset with `grant_year` (Oct-Sep fiscal year).
        """
        qs = qs if qs is not None else cls.objects.all()
        return qs.annotate(
            grant_year=models.Case(
                models.When(date__month__gte=10, then=models.F('date__year')),
                default=models.F('date__year') - 1,
                output_field=models.IntegerField()
            )
        )

    @classmethod
    def for_client_with_grant_year(cls, contact_id):
        """
        Full queryset used by oib_plan_list: filtered to contact, annotated and ordered.
        """
        client_services_and_related = cls.for_client(contact_id)
        return cls.with_grant_year_annotation(client_services_and_related) \
                  .order_by('-grant_year', 'oib_service_delivery_type__oib_service_delivery_type')

    @classmethod
    def in_grant_year(cls, contact_id, sdt_id, grant_year):
        """
        Events for a single contact + service_delivery_type in the provided grant_year.
        Use explicit date-range filtering (can use a date index) and then annotate with grant_year.
        Returns a queryset with select_related/prefetch applied.
        """
        start = date(grant_year, 10, 1)
        end = date(grant_year + 1, 9, 30)
        qs = cls.objects.filter(
            contacts__id=contact_id,
            oib_service_delivery_type__id=sdt_id,
            date__gte=start,
            date__lte=end
        ).select_related('oib_service_delivery_type').prefetch_related('services').order_by('-date')
        return qs

class OIBServiceEventOIBService(models.Model):
    oib_service_event = models.ForeignKey(OIBServiceEvent, on_delete=models.PROTECT)
    oib_service = models.ForeignKey(OIBService, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["oib_service_event", "oib_service"],
                name="unique_oib_service_event_oib_service"
            )
        ]

    def __str__(self):
        return f"{self.service_event} {self.oib_service}"

# QUESTION Does this even make sense?
#          ------------------------------------------------------------
# Presenter, guest, family member, caregiver, etc. are valid roles, but
# in order to use these, the participants to whom these roles apply must
# be added as a Contact beforehand... So until the Contact/Intake model
# is fixed, there is no point in adding other roles.
#
# The Contact model is a mess too, see NOTE/TODO there.
class OIBServiceEventContactRole(models.Model):
    oib_service_event_contact_role = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.oib_service_event_contact_role

class OIBServiceEventInstructorRole(models.Model):
    oib_service_event_instructor_role = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.oib_service_event_instructor_role

class OIBServiceEventInstructor(models.Model):
    oib_service_event = models.ForeignKey(OIBServiceEvent, on_delete=models.PROTECT)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT)
    oib_service_event_instructor_role = models.ForeignKey(OIBServiceEventInstructorRole, on_delete=models.PROTECT, default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["oib_service_event", "instructor"],
                name="unique_oib_service_event_instructor"
            )
        ]

    def __str__(self):
        return f"{self.service_event} {self.user} {self.role}"

class OIBServiceEventContact(models.Model):
    oib_service_event = models.ForeignKey(OIBServiceEvent, on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    oib_service_event_contact_role = models.ForeignKey(OIBServiceEventContactRole, on_delete=models.PROTECT, default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["oib_service_event", "contact"],
                name="unique_oib_service_event_contact"
            )
        ]

    def __str__(self):
        return f"{self.oib_service_event} {self.contact} {self.oib_service_event_contact_role}"

# OIB OUTCOMES
# ------------
# **OIB outcomes are independent of "plans".** They only appear as dropdowns on plans
# because that was the case in previous versions of LYNX, but quarterly OIB reports
# only have 4 outcomes per client and don't even mention "plans" once.
class OIBOutcomeType(models.Model):
    oib_outcome_type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.oib_outcome_type

class OIBOutcomeChoice(models.Model):
    oib_outcome_choice = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    # many-to-many relationships
    outcome_types = models.ManyToManyField(OIBOutcomeType, through='OIBOutcomeTypeChoice', through_fields=('oib_outcome_choice', 'oib_outcome_type'))

    def __str__(self):
        return self.oib_outcome_choice

# TODO 2025_09_06_1254 Document models; especially ones that have pre-set values
#                      in migrations.
#      =======================================================================
#      Added this one here before the OIB outcome-related models because they
#      are the perfect example. For example, `OIBOutcomeTypeChoice` has pre-set
#      combinations of OIB outcome types and their choices as some outcome types
#      have the same set of choices associated with them (see migration
#      0112_add_oiboutcometypechoice.py).

class OIBOutcomeTypeChoice(models.Model):
    oib_outcome_type = models.ForeignKey(OIBOutcomeType, on_delete=models.PROTECT)
    oib_outcome_choice = models.ForeignKey(OIBOutcomeChoice, on_delete=models.PROTECT)
    default_choice = models.BooleanField(default=False)  # new field
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["oib_outcome_type", "oib_outcome_choice"],
                name="unique_oib_outcome_type_choice"
            ),
            # enforce at most one row with default_choice=True per outcome type
            models.UniqueConstraint(
                fields=["oib_outcome_type"],
                condition=models.Q(default_choice=True),
                name="one_default_per_outcome_type"
            ),
        ]

    def clean(self):
        # application-level guard with a readable ValidationError
        if self.default_choice:
            qs = OIBOutcomeTypeChoice.objects.filter(
                oib_outcome_type=self.oib_outcome_type,
                default_choice=True
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise exc.ValidationError("Only one default choice is allowed per outcome type.")

    def __str__(self):
        return f"{self.oib_outcome_type} {self.oib_outcome_choice}"

# NOTE Why no FK to `OIBServiceEvent` or other models?
#      ----------------------------------------------------
# Because  the  relationships  between  SERVICES   and
# OUTCOMES are only loosely defined, and the  official
# procedure is to follow  up  with  a  survey  to  the
# client 60 days AFTER receiving services.

# NOTE Making this table immutable and append-only on the
#      application level (Django models) and not on the DB
#      level (i.e., migrations), in case some manual adjustments
#      are needed in the future.
class OIBOutcome(models.Model):
    oib_outcome_type_choice = models.ForeignKey(OIBOutcomeTypeChoice, on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)  # Active user
    oib_service_delivery_type = models.ForeignKey(OIBServiceDeliveryType, on_delete=models.PROTECT, null=True, blank=True)
    grant_year = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    # This field may seem superfluous if the model is append-only
    # and immutable, but it is good to have in case someone
    # or something tries (and able) to modify a record.
    modified = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.date} {self.time} {self.outcome_choice.name} {self.contact}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Updates are not allowed for OIBOutcome records.")
        super(OIBOutcome, self).save(*args, **kwargs)

    # TODO 2025_09_07_1700 This clearly has no effect as the view was able to delete records like it was
    #                      it was nothing.
    def delete(self, *args, **kwargs):
        raise ValueError("Deletions are not allowed for OIBOutcome records.")

    class Meta:
        verbose_name = "OIB Outcome"
        verbose_name_plural = "OIB Outcomes"


# === MARK FOR DELETION =====================================================
# Can't delete these until prod hasn't been migrated with 0131.
class BasePlanNote(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    note_date = models.DateField(blank=True, null=True)
    vision_screening = models.BooleanField(blank=True, default=False)
    treatment = models.BooleanField(blank=True, default=False)
    at_devices = models.BooleanField(blank=True, default=False)
    at_services = models.BooleanField(blank=True, default=False)
    independent_living = models.BooleanField(blank=True, default=False)
    orientation = models.BooleanField(blank=True, default=False)
    communications = models.BooleanField(blank=True, default=False)
    dls = models.BooleanField(blank=True, default=False)
    # other_services = models.BooleanField(blank=True, default=False)
    support = models.BooleanField(blank=True, default=False)
    advocacy = models.BooleanField(blank=True, default=False)
    counseling = models.BooleanField(blank=True, default=False)
    information = models.BooleanField(blank=True, default=False)
    services = models.BooleanField(blank=True, default=False)
    retreat = models.BooleanField(blank=True, default=False)
    in_home = models.BooleanField(blank=True, default=False)
    seminar = models.BooleanField(blank=True, default=False)
    modesto = models.BooleanField(blank=True, default=False)
    group = models.BooleanField(blank=True, default=False)
    community = models.BooleanField(blank=True, default=False)
    fiscal_year = models.CharField(max_length=15, blank=True, null=True)
    quarter = models.IntegerField(blank=True, null=True)
    class_hours = models.FloatField(blank=True, null=True, choices=SIP_UNITS)
    # TODO Remove as this is superfluous - there is already a ForeignKey to User.
    instructor = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    history = HistoricalRecords(inherit=True)

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})

    # TODO Add string representation methods to other models as well.
    def __str__(self):
        return str(self.note_date)

    class Meta:
        abstract = True


class SipNote(BasePlanNote):
    sip_plan = models.ForeignKey('SipPlan', on_delete=models.CASCADE, blank=True, null=True)


class Sip1854Note(BasePlanNote):
    sip_plan = models.ForeignKey('Sip1854Plan', on_delete=models.CASCADE, blank=True, null=True)


class BasePlan(models.Model):
    PLANS = (("Plan not complete", "Plan not complete"),
             ("Plan complete, feeling more confident in ability to maintain living situation",
              "Plan complete, feeling more confident in ability to maintain living situation"),
             ("Plan complete, no difference in ability to maintain living situation",
              "Plan complete, no difference in ability to maintain living situation"),
             ("Plan complete, feeling less confident in ability to maintain living situation",
              "Plan complete, feeling less confident in ability to maintain living situation"))
    ASSESSMENTS = (("Not assessed", "Not assessed"), ("Assessed with improved independence",
                                                      "Assessed with improved independence"),
                   ("Assessed and maintained independence", "Assessed and maintained independence"),
                   ("Assessed with decreased independence", "Assessed with decreased independence"))
    EMPLOYMENT = (("Not Interested in Employment", "Not Interested in Employment"),
                  ("Less Likely to Seek Employment", "Less Likely to Seek Employment"),
                  ("Unsure about Seeking Employment", "Unsure about Seeking Employment"),
                  ("More Likely to Seek Employment", "More Likely to Seek Employment"))
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)
    at_services = models.BooleanField(blank=True, default=False)
    independent_living = models.BooleanField(blank=True, default=False)
    orientation = models.BooleanField(blank=True, default=False)
    communications = models.BooleanField(blank=True, default=False)
    dls = models.BooleanField(blank=True, default=False)
    advocacy = models.BooleanField(blank=True, default=False)
    counseling = models.BooleanField(blank=True, default=False)
    information = models.BooleanField(blank=True, default=False)
    other_services = models.BooleanField(blank=True, default=False)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    plan_date = models.DateField(blank=True, null=True)
    support_services = models.BooleanField(blank=True, default=False)
    living_plan_progress = models.CharField(
        max_length=150,
        choices=PLANS,
        blank=True,
        null=True,
        default="Plan not complete"
    )
    community_plan_progress = models.CharField(
        max_length=150,
        choices=PLANS,
        blank=True,
        null=True,
        default="Plan not complete"
    )
    employment_outcomes = models.CharField(max_length=150, choices=EMPLOYMENT, blank=True, null=True, default="Not Interested in Employment")
    at_outcomes = models.CharField(max_length=150, choices=ASSESSMENTS, blank=True, null=True, default="Not assessed")
    ila_outcomes = models.CharField(max_length=150, choices=ASSESSMENTS, blank=True, null=True, default="Not assessed")
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.plan_name

    def get_absolute_url(self):
        return reverse('lynx:contact_show', kwargs={'pk': self.contact_id})

    class Meta:
            abstract = True

class SipPlan(BasePlan):
    pass


class Sip1854Plan(BasePlan):
    pass



# vim: set foldmethod=marker foldmarker={{-,}}-:
