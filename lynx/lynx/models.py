from django.db import models

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


# Contact information. For Clients, Employees and Volunteers.
class Contact(models.Model):
    name = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    gender = models.CharField(max_length=50)
    birth_date = models.DateField()
    ssn = models.CharField(max_length=15)
    ethnicity = models.CharField(max_length=50)
    day_phone = models.CharField(max_length=20)
    night_phone = models.CharField(max_length=20)
    other_phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)
    email = models.EmailField()
    do_not_contact = models.CharField(max_length=150)
    deceased = models.BinaryField()
    do_not_contact_two = models.CharField(max_length=150)
    contact_notes = models.TextField()


#Employee information. Contact information in Contact table, addresses in Address table.
class Employee(models.Model):
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    employee_type = models.CharField(max_length=150)


#Addresses for Contacts.
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
    billing = models.BinaryField() #Only applies to employees
    address_notes = models.TextField()


class Billing(models.Model):
    employee_id = models.ForeignKey('Employee', on_delete=models.CASCADE)
    invoice_date = models.DateField()


#Intake questionairre
class Intake(models.Model):
    contact_id = models.ForeignKey('Contact', on_delete=models.CASCADE)
    created = models.DateField()
    modified = models.DateField()
    intake_date = models.DateField()
    intake_type = models.CharField(max_length=150)
    age_group = models.CharField(max_length=150)
    volunteer_driving = models.BinaryField()
    volunteer_reading = models.BinaryField()
    volunteer_shopping = models.BinaryField()
    volunteer_errands = models.BinaryField()
    volunteer_assistant = models.BinaryField()
    volunteer_other = models.CharField(max_length=150)
    volunteer_skills_test = models.CharField(max_length=150)
    preferred_medium = models.CharField(max_length=150)
    notes = models.TextField()
    training = models.CharField(max_length=250)
    orientation = models.CharField(max_length=250)
    confidentiality = models.CharField(max_length=250)
    dmv = models.CharField(max_length=250)
    work = models.TextField()
    member_name = models.CharField(max_length=250)
    active = models.BinaryField()
    crime = models.BinaryField()
    crime_info = models.CharField(max_length=250)
    crime_other = models.CharField(max_length=250)
    parole = models.BinaryField()
    parole_info = models.CharField(max_length=250)
    crime_history = models.TextField()



