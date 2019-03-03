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


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


# Contact information. For Clients, Employees and Volunteers.
class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    do_not_contact = models.BinaryField()
    deceased = models.BinaryField()
    remove_mailing = models.BinaryField()
    contact_notes = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Email (models.Model):
    EMAIL_TYPES = (("Work", "Work"), ("Personal", "Personal"))

    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    email = models.EmailField()
    type = models.CharField(max_length=25, choices=EMAIL_TYPES)
    active = models.BinaryField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Phone (models.Model):
    PHONE_TYPES = (("Work", "Work"), ("Home", "Home"), ("Cell", "Cell"), ("Evening", "Evening"), ("Fax", "Fax"))

    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    type = models.CharField(max_length=25, choices=PHONE_TYPES)
    active = models.BinaryField()
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
    name = models.CharField(max_length=150)
    address_one = models.CharField(max_length=150)
    address_two = models.CharField(max_length=150)
    suite = models.CharField(max_length=50)
    city = models.CharField(max_length=75)
    state = models.CharField(max_length=25, choices=STATES)
    zip_code = models.CharField(max_length=15)
    county = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    region = models.CharField(max_length=150)
    cross_streets = models.CharField(max_length=150)
    bad_address = models.BinaryField()
    billing = models.BinaryField()  # Only applies to employees
    address_notes = models.TextField()
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
    intake_date = models.DateField()
    intake_type = models.CharField(max_length=150)
    age_group = models.CharField(max_length=150)
    gender = models.CharField(max_length=50)
    birth_date = models.DateField()
    ssn = models.CharField(max_length=15)
    ethnicity = models.CharField(max_length=50)
    income = models.CharField(max_length=25, choices=INCOMES)
    first_language = models.CharField(max_length=50)
    second_language = models.CharField(max_length=50)
    other_languages = models.CharField(max_length=150)
    education = models.CharField(max_length=150)
    living_arrangement= models.CharField(max_length=150)
    residence_type= models.CharField(max_length=150)
    preferred_medium = models.CharField(max_length=150)
    performs_tasks= models.CharField(max_length=150)
    notes = models.TextField()
    training = models.CharField(max_length=250)
    orientation = models.CharField(max_length=250)
    confidentiality = models.CharField(max_length=250)
    dmv = models.CharField(max_length=250)
    work_history = models.TextField()
    member_name = models.CharField(max_length=250)
    active = models.BinaryField()
    crime = models.BinaryField()
    crime_info = models.CharField(max_length=250)
    crime_other = models.CharField(max_length=250)
    parole = models.BinaryField()
    parole_info = models.CharField(max_length=250)
    crime_history = models.TextField()
    previous_training = models.TextField()
    training_goals = models.TextField()
    training_preferences = models.TextField()
    other = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey('User', on_delete=models.SET(get_sentinel_user))


class Medical(models.Model):
    intake_id = models.ForeignKey('Intake', on_delete=models.CASCADE)
    eye_condition = models.CharField(max_length=250)
    eye_condition_date = models.DateField()
    degree = models.CharField(max_length=250)
    prognosis = models.CharField(max_length=250)
    diabetes = models.BinaryField()
    dialysis = models.BinaryField()
    hearing_loss = models.BinaryField()
    mobility = models.BinaryField()
    stroke = models.BinaryField()
    seizure = models.BinaryField()
    heart = models.BinaryField()
    high_bp = models.BinaryField()
    neuropathy = models.BinaryField()
    pain = models.BinaryField()
    asthma = models.BinaryField()
    cancer = models.BinaryField()
    allergies = models.CharField(max_length=250)
    mental_health = models.CharField(max_length=250)
    substance_abuse= models.BinaryField()
    memory_loss= models.BinaryField()
    learning_disability= models.BinaryField()
    other = models.CharField(max_length=250)
    medications = models.CharField(max_length=250)
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
