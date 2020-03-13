from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now

from datetime import datetime, date


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

REGIONS = (("Sacramento", "Sacramento"), ("Fresno", "Fresno"), ("Chico", "Chico"), ("Diablo", "Diablo"))

GENDERS = (("Female", "Female"), ("Male", "Male"), ("Non-Binary", "Non-Binary"),
           ("Gender Non-Conforming", "Gender Non-Conforming"), ("Other (in notes)", "Other (in notes)"),
           ("Prefer Not to Say", "Prefer Not to Say"), )

ETHNICITIES = (("White", "White"), ("Hispanic or Latino", "Hispanic or Latino"),
               ("Black or African American", "Black or African American"), ("Asian", "Asian"),
               ("American Indian or Alaska Native", "American Indian or Alaska Native"),
               ("Native Hawaiian or Other Pacific Islander", "Native Hawaiian or Other Pacific Islander"),
               ("Other", "Other"))

MAILINGS = (("N/A", "N/A"), ("Print", "Print"), ("Large Print", "Large Print"), ("Braille", "Braille"),
            ("E-Mail", "E-Mail"), ("Cassette", "Cassette"))

TRINARY = (('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other'))

MONTHS = (("January", "January"), ("February", "February"), ("March", "March"), ("April", "April"),
            ("May", "May"), ("June", "June"), ("July", "July"), ("August", "August"), ("September", "September"),
            ("October", "October"), ("November", "November"), ("December", "December"))

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

EDUCATION = (("None", "None"), ("GED", "GED"), ("High School", "High School"), ("Associates", "Associates"),
             ("Bachelors", "Bachelors"), ("Masters", "Masters"), ("Doctorate", "Doctorate"))

PRONOUNS = (("He/Him", "He/Him"), ("She/Her", "She/Her"), ("They/Them", "They/Them"), ("Ve/Ver", "Ve/Ver"),
            ("Xe/Xim", "Xe/Xim"), ("Ze/Hir", "Ze/Hir"), ("Other (in notes)", "Other (in notes)"))

UNITS = (("1", "15 Minutes"), ("2", "30 Minutes"), ("3", "45 Minutes"), ("4", "1 Hour"), ("5", "1 Hour 15 Minutes"),
         ("6", "1 Hour 30 Minutes"), ("7", "1 Hour 45 Minutes"), ("8", "2 Hours"), ("9", "2 Hours 15 Minutes"),
         ("10", "2 Hours 30 Minutes"), ("11", "2 Hours 45 Minutes"), ("12", "3 Hours"), ("13", "3 Hours 15 Minutes"),
         ("14", "3 Hours 30 Minutes"), ("15", "3 Hours 45 Minutes"), ("16", "4 Hours"), ("17", "4 Hours 15 Minutes"),
         ("18", "4 Hours 30 Minutes"), ("19", "4 Hours 45 Minutes"), ("20", "5 Hours"), ("21", "5 Hours 15 Minutes"),
         ("22", "5 Hours 30 Minutes"), ("23", "5 Hours 45 Minutes"), ("24", "6 Hours"), ("25", "6 Hours 15 Minutes"),
         ("26", "6 Hours 30 Minutes"), ("27", "6 Hours 45 Minutes"), ("28", "7 Hours"), ("29", "7 Hours 15 Minutes"),
         ("30", "7 Hours 30 Minutes"), ("31", "7 Hours 45 Minutes"), ("32", "8 Hours"))

SALUTATIONS = (("Mr.", "Mr."), ("Mrs.", "Mrs."), ("Miss", "Miss"), ("Ms.", "Ms."), ("Dr.", "Dr."), ("Prof.", "Prof."),
               ("Rev.", "Rev."))


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


# Contact information. For Clients, Employees and Volunteers.
class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    salutation = models.CharField(max_length=25, choices=SALUTATIONS, blank=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    do_not_contact = models.BooleanField(blank=True, default=False)
    donor = models.BooleanField(blank=True, default=False)
    deceased = models.BooleanField(blank=True, default=False)
    remove_mailing = models.BooleanField(blank=True, default=False)
    active = models.BooleanField(blank=True, default=True)
    sip_client = models.BooleanField(blank=True, default=False)
    core_client = models.BooleanField(blank=True, default=False)
    careers_plus = models.BooleanField(blank=True, default=False)
    careers_plus_youth = models.BooleanField(blank=True, default=False)
    volunteer = models.BooleanField(blank=True, default=False)
    access_news = models.BooleanField(blank=True, default=False)
    other_services = models.BooleanField(blank=True, default=False)
    contact_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.id


class Email (models.Model):
    EMAIL_TYPES = (("Work", "Work"), ("Personal", "Personal"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    email = models.EmailField()
    email_type = models.CharField(max_length=25, choices=EMAIL_TYPES, blank=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contact_emails', null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


class Phone (models.Model):
    PHONE_TYPES = (("Work", "Work"), ("Home", "Home"), ("Cell", "Cell"), ("Evening", "Evening"), ("Fax", "Fax"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    phone_type = models.CharField(max_length=25, choices=PHONE_TYPES, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


# Employee information. Contact information in Contact table, addresses in Address table.
class Employee(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    employee_type = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


# Addresses for Contacts.
class Address(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
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
    billing = models.BooleanField(blank=True, default=False)  # Only applies to employees
    preferred_medium = models.CharField(max_length=150, blank=True, choices=MAILINGS, null=True)
    address_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name_plural = 'Addresses'

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


class Billing(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    invoice_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


# Intake questionnaire
class Intake(models.Model):
    INCOMES = (("<$12,500", "<$12,500"), ("$12,500-$25,000", "$12,500-$25,000"), ("$25,001-$50,000", "$25,001-$50,000"),
               ("$50,001-$75,000", "$50,001-$75,000"), ("$75,001-$100,000", "$75,001-$100,000"),
               ("$100,001-$125,000", "$100,001-$125,000"), ("$125,001-$1150,000", "$125,001-$150,000"),
               (">$150,000", ">$150,000"))

    LIVING = (("Live Alone", "Live Alone"), ("Live With Spouse", "Live With Spouse"),
              ("Live With Other", "Live With Other"), ("Homeless", "Homeless"))

    RESIDENCE = (("Private Residence", "Private Residence"), ("Community Residential", "Community Residential"),
                 ("Assisted Living", "Assisted Living"), ("Skilled Nursing Care", "Skilled Nursing Care"),
                 ("Homeless", "Homeless"))

    PROGNOSIS = (("Stable", "Stable"), ("Diminishing", "Diminishing"))

    DEGREE = (("Totally Blind (NP or NLP)", "Totally Blind (NP or NLP)"), ("Legally Blind", "Legally Blind"),
              ("Severe Visual Impairment", "Severe Visual Impairment"), ("Low Vision", "Low Vision"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_date = models.DateField(default=date.today)
    intake_type = models.CharField(max_length=150, blank=True, null=True)
    age_group = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, choices=GENDERS, null=True)
    pronouns = models.CharField(max_length=150, blank=True, choices=PRONOUNS, null=True)
    birth_date = models.DateField(blank=True, null=True)
    ssn = models.CharField(max_length=15, blank=True, null=True)
    ethnicity = models.CharField(max_length=50, blank=True, choices=ETHNICITIES, null=True)
    other_ethnicity = models.CharField(max_length=50, blank=True, null=True)
    income = models.CharField(max_length=25, choices=INCOMES, blank=True, null=True)
    first_language = models.CharField(max_length=50, blank=True, choices=LANGUAGES, null=True)
    second_language = models.CharField(max_length=50, blank=True, choices=LANGUAGES, null=True)
    other_languages = models.CharField(max_length=150, blank=True, null=True)
    education = models.CharField(max_length=150, blank=True, choices=EDUCATION, null=True)
    living_arrangement = models.CharField(max_length=150, blank=True, choices=LIVING, null=True)
    residence_type = models.CharField(max_length=150, blank=True, choices=RESIDENCE, null=True)
    performs_tasks = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    training = models.CharField(max_length=250, blank=True, null=True)
    orientation = models.CharField(max_length=250, blank=True, null=True)
    confidentiality = models.CharField(max_length=250, blank=True, null=True)
    dmv = models.CharField(max_length=250, blank=True, null=True)
    work_history = models.TextField(blank=True, null=True)
    veteran = models.BooleanField(blank=True, default=False)
    member_name = models.CharField(max_length=250, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True, default=True)
    crime = models.BooleanField(blank=True, default=False)
    crime_info = models.TextField(blank=True, null=True)
    crime_other = models.CharField(max_length=250, blank=True, null=True)
    parole = models.BooleanField(blank=True, default=False)
    parole_info = models.CharField(max_length=250, blank=True, null=True)
    crime_history = models.TextField(blank=True, null=True)
    previous_training = models.TextField(blank=True, null=True)
    training_goals = models.TextField(blank=True, null=True)
    training_preferences = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    eye_condition = models.CharField(max_length=250, blank=True, null=True)
    eye_condition_date = models.DateField(null=True, blank=True)
    degree = models.CharField(max_length=250, blank=True, choices=DEGREE, null=True)
    prognosis = models.CharField(max_length=250, blank=True, choices=PROGNOSIS, null=True)
    diabetes = models.BooleanField(blank=True, default=False)
    dialysis = models.BooleanField(blank=True, default=False)
    hearing_loss = models.BooleanField(blank=True, default=False)
    mobility = models.BooleanField(blank=True, default=False)
    stroke = models.BooleanField(blank=True, default=False)
    seizure = models.BooleanField(blank=True, default=False)
    heart = models.BooleanField(blank=True, default=False)
    arthritis = models.BooleanField(blank=True, default=False)
    high_bp = models.BooleanField(blank=True, default=False)
    neuropathy = models.BooleanField(blank=True, default=False)
    pain = models.BooleanField(blank=True, default=False)
    asthma = models.BooleanField(blank=True, default=False)
    cancer = models.BooleanField(blank=True, default=False)
    musculoskeletal = models.BooleanField(blank=True, default=False)
    alzheimers = models.BooleanField(blank=True, default=False)
    allergies = models.CharField(max_length=250, blank=True, null=True)
    mental_health = models.CharField(max_length=250, blank=True, null=True)
    substance_abuse = models.BooleanField(blank=True, default=False)
    memory_loss = models.BooleanField(blank=True, default=False)
    learning_disability = models.BooleanField(blank=True, default=False)
    other_medical = models.CharField(max_length=250, blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    employment_goals = models.TextField(blank=True, null=True)
    hired = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


class Referral(models.Model):
    intake = models.ForeignKey('Intake', on_delete=models.CASCADE)
    source = models.CharField(max_length=250, null=True)
    name = models.CharField(max_length=250, null=True)
    referral_date = models.DateField(null=True, default=date.today)
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class IntakeNote(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


# Addresses for Contacts.
class EmergencyContact(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    emergency_address_one = models.CharField(max_length=150, blank=True, null=True)
    emergency_address_two = models.CharField(max_length=150, blank=True, null=True)
    emergency_city = models.CharField(max_length=75, blank=True, null=True)
    emergency_state = models.CharField(max_length=25, choices=STATES, default='California', blank=True, null=True)
    emergency_zip_code = models.CharField(max_length=15, blank=True, null=True)
    emergency_country = models.CharField(max_length=150, blank=True, null=True)
    phone_day = models.CharField(max_length=150, blank=True, null=True)
    phone_other = models.CharField(max_length=150, blank=True, null=True)
    emergency_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id


class Authorization(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_service_area = models.ForeignKey('IntakeServiceArea', on_delete=models.CASCADE)
    authorization_number = models.CharField(max_length=150, blank=True, null=True)
    authorization_type = models.CharField(max_length=25, choices=(("Hours", "Hours"), ("Classes", "Classes")), blank=True, null=True)
    start_date = models.DateField(blank=True, null=True, default=date.today)
    end_date = models.DateField(blank=True, null=True, default=date.today)
    total_time = models.CharField(max_length=150, blank=True, null=True)
    # monthly_time = models.CharField(max_length=150, blank=True, null=True)
    billing_name = models.ForeignKey('BillingName', on_delete=models.CASCADE)
    billing_rate = models.CharField(max_length=150, blank=True, null=True)
    outside_agency = models.ForeignKey('OutsideAgency', on_delete=models.CASCADE)
    student_plan = models.CharField(max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class OutsideAgency(models.Model):
    agency = models.CharField(max_length=150, blank=True, null=True)
    contact = models.CharField(max_length=150, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name_plural = 'Outside Agencies'

    def __str__(self):
        return '%s - %s' % (self.contact, self.agency)


class IntakeServiceArea(models.Model):
    agency = models.CharField(max_length=150, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return self.agency


class BillingName(models.Model):
    agency = models.CharField(max_length=150, blank=True, null=True)
    cost = models.CharField(max_length=50, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return '%s ($%s)' % (self.agency, self.cost)


class ProgressReport(models.Model):
    month = models.CharField(max_length=25, choices=MONTHS, blank=True, null=True)
    authorization = models.ForeignKey('Authorization', on_delete=models.CASCADE)
    instructor = models.CharField(max_length=150, blank=True, null=True)
    accomplishments = models.TextField(blank=True, null=True)
    remaining_objectives = models.TextField(blank=True, null=True)
    estimated_hours = models.TextField(blank=True, null=True)
    client_behavior = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class LessonNote(models.Model):
    authorization = models.ForeignKey('Authorization', on_delete=models.CASCADE)
    date = models.DateField(default=date.today, null=True)
    attendance = models.CharField(max_length=150, blank=True, choices=(('Other', 'Other'), ('Present', 'Present'), ('Absent', 'Absent')), null=True)
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


class SipNote(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    note_date = models.DateField(blank=True, null=True, default=date.today)
    vision_screening = models.BooleanField(blank=True, default=False)
    treatment = models.BooleanField(blank=True, default=False)
    at_devices = models.BooleanField(blank=True, default=False)
    at_services = models.BooleanField(blank=True, default=False)
    independent_living = models.BooleanField(blank=True, default=False)
    orientation = models.BooleanField(blank=True, default=False)
    communications = models.BooleanField(blank=True, default=False)
    dls = models.BooleanField(blank=True, default=False)
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
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def get_absolute_url(self):
        return "/lynx/client/%i" % self.contact_id