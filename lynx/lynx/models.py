from django.db import models
from django.contrib.auth import get_user_model

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
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    do_not_contact = models.BooleanField(blank=True)
    deceased = models.BooleanField(blank=True)
    remove_mailing = models.BooleanField(blank=True)
    contact_notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Email (models.Model):
    EMAIL_TYPES = (("Work", "Work"), ("Personal", "Personal"))

    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    email = models.EmailField()
    type = models.CharField(max_length=25, choices=EMAIL_TYPES, blank=True)
    active = models.BooleanField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Phone (models.Model):
    PHONE_TYPES = (("Work", "Work"), ("Home", "Home"), ("Cell", "Cell"), ("Evening", "Evening"), ("Fax", "Fax"))

    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    type = models.CharField(max_length=25, choices=PHONE_TYPES, blank=True)
    active = models.BooleanField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


# Employee information. Contact information in Contact table, addresses in Address table.
class Employee(models.Model):
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    employee_type = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


# Addresses for Contacts.
class Address(models.Model):
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    address_one = models.CharField(max_length=150, blank=True)
    address_two = models.CharField(max_length=150, blank=True)
    suite = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=75, blank=True)
    state = models.CharField(max_length=25, choices=STATES, default='California', blank=True)
    zip_code = models.CharField(max_length=15, blank=True)
    county = models.CharField(max_length=150, choices=COUNTIES, blank=True)
    country = models.CharField(max_length=150, blank=True)
    region = models.CharField(max_length=150, blank=True)
    cross_streets = models.CharField(max_length=150, blank=True)
    bad_address = models.BooleanField(blank=True)
    billing = models.BooleanField(blank=True)  # Only applies to employees
    address_notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Billing(models.Model):
    employee_id = models.ForeignKey('Employee', on_delete=models.CASCADE)
    invoice_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


# Intake questionnaire
class Intake(models.Model):
    INCOMES = (("<$25,000", "<$25,000"), ("$25,001-$50,000", "$25,001-$50,000"),
               ("$50,001-$75,000", "$50,001-$75,000"), ("$75,001-$100,000", "$75,001-$100,000"),
               ("$100,001-$125,000", "$100,001-$125,000"), ("$125,001-$1150,000", "$125,001-$150,000"),
               (">$150,000", ">$150,000"))

    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    intake_date = models.DateField(blank=True)
    intake_type = models.CharField(max_length=150, blank=True)
    age_group = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=50, blank=True, choices=GENDERS)
    birth_date = models.DateField(blank=True)
    ssn = models.CharField(max_length=15, blank=True)
    ethnicity = models.CharField(max_length=50, blank=True)
    other_ethnicity = models.CharField(max_length=50, blank=True)
    income = models.CharField(max_length=25, choices=INCOMES, blank=True)
    first_language = models.CharField(max_length=50, blank=True)
    second_language = models.CharField(max_length=50, blank=True)
    other_languages = models.CharField(max_length=150, blank=True)
    education = models.CharField(max_length=150, blank=True)
    living_arrangement= models.CharField(max_length=150, blank=True)
    residence_type= models.CharField(max_length=150, blank=True)
    preferred_medium = models.CharField(max_length=150, blank=True, choices=MAILINGS)
    performs_tasks= models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    training = models.CharField(max_length=250, blank=True)
    orientation = models.CharField(max_length=250, blank=True)
    confidentiality = models.CharField(max_length=250, blank=True)
    dmv = models.CharField(max_length=250, blank=True)
    work_history = models.TextField(blank=True)
    veteran = models.BooleanField(blank=True)
    member_name = models.CharField(max_length=250, blank=True)
    active = models.BooleanField(blank=True)
    crime = models.BooleanField(blank=True)
    crime_info = models.TextField(blank=True)
    crime_other = models.CharField(max_length=250, blank=True)
    parole = models.BooleanField(blank=True)
    parole_info = models.CharField(max_length=250, blank=True)
    crime_history = models.TextField(blank=True)
    previous_training = models.TextField(blank=True)
    training_goals = models.TextField(blank=True)
    training_preferences = models.TextField(blank=True)
    other = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Medical(models.Model):
    intake_id = models.ForeignKey('Intake', on_delete=models.CASCADE)
    eye_condition = models.CharField(max_length=250, blank=True)
    eye_condition_date = models.DateField()
    degree = models.CharField(max_length=250, blank=True)
    prognosis = models.CharField(max_length=250, blank=True)
    diabetes = models.BooleanField(blank=True)
    dialysis = models.BooleanField(blank=True)
    hearing_loss = models.BooleanField(blank=True)
    mobility = models.BooleanField(blank=True)
    stroke = models.BooleanField(blank=True)
    seizure = models.BooleanField(blank=True)
    heart = models.BooleanField(blank=True)
    high_bp = models.BooleanField(blank=True)
    neuropathy = models.BooleanField(blank=True)
    pain = models.BooleanField(blank=True)
    asthma = models.BooleanField(blank=True)
    cancer = models.BooleanField(blank=True)
    allergies = models.CharField(max_length=250, blank=True)
    mental_health = models.CharField(max_length=250, blank=True)
    substance_abuse= models.BooleanField(blank=True)
    memory_loss= models.BooleanField(blank=True)
    learning_disability= models.BooleanField(blank=True)
    other = models.CharField(max_length=250, blank=True)
    medications = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Referral(models.Model):
    intake_id = models.ForeignKey('Intake', on_delete=models.CASCADE)
    source = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    referral_date = models.DateField()
    created = models.DateTimeField()
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class IntakeNote(models.Model):
    intake_id = models.ForeignKey('Intake', on_delete=models.CASCADE)
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class User(models.Model):
    username = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


# Addresses for Contacts.
class EmergencyContact(models.Model):
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)
    address_one = models.CharField(max_length=150, blank=True)
    address_two = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=75, blank=True)
    state = models.CharField(max_length=25, choices=STATES, default='California', blank=True)
    zip_code = models.CharField(max_length=15, blank=True)
    country = models.CharField(max_length=150, blank=True)
    phone_day = models.CharField(max_length=150, blank=True)
    phone_other = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))
