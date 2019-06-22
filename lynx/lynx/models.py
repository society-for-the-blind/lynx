from django.db import models
from django.contrib.auth import get_user_model

from django.conf import settings

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

GENDERS = (("Female", "Female"), ("Male", "Male"), ("Non-Binary", "Non-Binary"), ("Other", "Other"))

ETHNICITIES = (("Data not recorded", "Data not recorded"), ("White", "White"),
               ("Black or African American", "Black or African American"), ("Asian", "Asian"),
               ("American Indian or Alaska Native", "American Indian or Alaska Native"),
               ("Native Hawaiian or Other Pacific Islander", "Native Hawaiian or Other Pacific Islander"),
               ("Hispanic or Latino", "Hispanic or Latino"), ("Other", "Other"))

MAILINGS = (("N/A", "N/A"), ("Print", "Print"), ("Large Print", "Large Print"), ("Braille", "Braille"),
            ("E-Mail", "E-Mail"), ("Cassette", "Cassette"))

TRINARY = (('Yes', 'Yes'), ('No', 'No'), ('Other', 'Other'))



def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


# Contact information. For Clients, Employees and Volunteers.
class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True, null=True)
    do_not_contact = models.BooleanField(blank=True, default=False)
    donor = models.BooleanField(blank=True, default=False)
    deceased = models.BooleanField(blank=True, default=False)
    remove_mailing = models.BooleanField(blank=True, default=False)
    contact_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Email (models.Model):
    EMAIL_TYPES = (("Work", "Work"), ("Personal", "Personal"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    email = models.EmailField()
    type = models.CharField(max_length=25, choices=EMAIL_TYPES, blank=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contact_emails', null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class Phone (models.Model):
    PHONE_TYPES = (("Work", "Work"), ("Home", "Home"), ("Cell", "Cell"), ("Evening", "Evening"), ("Fax", "Fax"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    type = models.CharField(max_length=25, choices=PHONE_TYPES, blank=True, null=True)
    active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


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
    address_notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name_plural = 'Addresses'


class Billing(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    invoice_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


# Intake questionnaire
class Intake(models.Model):
    INCOMES = (("<$25,000", "<$25,000"), ("$25,001-$50,000", "$25,001-$50,000"),
               ("$50,001-$75,000", "$50,001-$75,000"), ("$75,001-$100,000", "$75,001-$100,000"),
               ("$100,001-$125,000", "$100,001-$125,000"), ("$125,001-$1150,000", "$125,001-$150,000"),
               (">$150,000", ">$150,000"))

    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_date = models.DateField(blank=True, null=True)
    intake_type = models.CharField(max_length=150, blank=True, null=True)
    age_group = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, choices=GENDERS, null=True)
    birth_date = models.DateField(blank=True, null=True)
    ssn = models.CharField(max_length=15, blank=True, null=True)
    ethnicity = models.CharField(max_length=50, blank=True, null=True)
    other_ethnicity = models.CharField(max_length=50, blank=True, null=True)
    income = models.CharField(max_length=25, choices=INCOMES, blank=True, null=True)
    first_language = models.CharField(max_length=50, blank=True, null=True)
    second_language = models.CharField(max_length=50, blank=True, null=True)
    other_languages = models.CharField(max_length=150, blank=True, null=True)
    education = models.CharField(max_length=150, blank=True, null=True)
    living_arrangement = models.CharField(max_length=150, blank=True, null=True)
    residence_type = models.CharField(max_length=150, blank=True, null=True)
    preferred_medium = models.CharField(max_length=150, blank=True, choices=MAILINGS, null=True)
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
    eye_condition_date = models.DateField(null=True)
    degree = models.CharField(max_length=250, blank=True, null=True)
    prognosis = models.CharField(max_length=250, blank=True, null=True)
    diabetes = models.BooleanField(blank=True, default=False)
    dialysis = models.BooleanField(blank=True, default=False)
    hearing_loss = models.BooleanField(blank=True, default=False)
    mobility = models.BooleanField(blank=True, default=False)
    stroke = models.BooleanField(blank=True, default=False)
    seizure = models.BooleanField(blank=True, default=False)
    heart = models.BooleanField(blank=True, default=False)
    high_bp = models.BooleanField(blank=True, default=False)
    neuropathy = models.BooleanField(blank=True, default=False)
    pain = models.BooleanField(blank=True, default=False)
    asthma = models.BooleanField(blank=True, default=False)
    cancer = models.BooleanField(blank=True, default=False)
    allergies = models.CharField(max_length=250, blank=True, null=True)
    mental_health = models.CharField(max_length=250, blank=True, null=True)
    substance_abuse = models.BooleanField(blank=True, default=False)
    memory_loss = models.BooleanField(blank=True, default=False)
    learning_disability = models.BooleanField(blank=True, default=False)
    other_medical = models.CharField(max_length=250, blank=True, null=True)
    medications = models.CharField(max_length=250, blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    hired = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class Referral(models.Model):
    intake = models.ForeignKey('Intake', on_delete=models.CASCADE)
    source = models.CharField(max_length=250, null=True)
    name = models.CharField(max_length=250, null=True)
    referral_date = models.DateField(null=True)
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class IntakeNote(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    note = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


# Addresses for Contacts.
class EmergencyContact(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    address_one = models.CharField(max_length=150, blank=True, null=True)
    address_two = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=75, blank=True, null=True)
    state = models.CharField(max_length=25, choices=STATES, default='California', blank=True, null=True)
    zip_code = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=150, blank=True, null=True)
    phone_day = models.CharField(max_length=150, blank=True, null=True)
    phone_other = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user))


class Authorization(models.Model):
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_service_area = models.ForeignKey('IntakeServiceArea', on_delete=models.CASCADE)
    authorization_number = models.CharField(max_length=150, blank=True, null=True)
    authorization_type = models.CharField(max_length=25, choices=(("Hours", "Hours"), ("Classes", "Classes")), blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    total_time = models.CharField(max_length=150, blank=True, null=True)
    monthly_time = models.CharField(max_length=150, blank=True, null=True)
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
