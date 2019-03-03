from django import forms


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


class IntakeForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    initial = forms.CharField(label='Middle Initial', max_length=10)
    last_name = forms.CharField(label='Last Name', max_length=100)
    company = forms.CharField(label='Company', max_length=100)
    address_one = forms.CharField(label='Address Line 1', max_length=100)
    address_two = forms.CharField(label='Address Line 2', max_length=100)
    apartment = forms.CharField(label='Suite or Apartment Number', max_length=100)
    state = forms.ChoiceField(label='State', choices=STATES, initial='California')
    zip = forms.CharField(label='Zip Code', max_length=100)
    county = forms.ChoiceField(label='County', choices=COUNTIES, initial='Sacramento')
    region = forms.ChoiceField(label='SIR Region', choices=REGIONS)
    cross_street = forms.CharField(label='Major Cross Street', max_length=100)
    phone_day = forms.CharField(label='Daytime Phone', max_length=100)
    phone_night = forms.CharField(label='Evening Phone', max_length=100)
    phone_other = forms.CharField(label='Other Phone', max_length=100)
    no_mail = forms.CharField(label='Remove from Mailing List', max_length=100)
    gender = forms.ChoiceField(label='Gender', choices=GENDERS)
    ethnicity = forms.ChoiceField(label='Ethnicity', choices=ETHNICITIES)
    other_ethnicity = forms.CharField(label='Ethnicity if Other', max_length=100)
    birthdate = forms.CharField(label='Birthdate', max_length=100)
    ssn = forms.CharField(label='Social Security (use ###-##-####)', max_length=15)
    mailings = forms.ChoiceField(label='Medium for Mailings', choices=MAILINGS)
    crime = forms.ChoiceField(label='Have you been convicted of a crime?', choices=TRINARY, initial='No')
    crime_other = forms.CharField(label='Criminal Conviction if Other', max_length=100)
    crime_info = forms.CharField(label='If yes, what and when did the convictions occur? '
                                       'What county did this conviction occur in?', max_length=250)
    parole = forms.ChoiceField(label='Are you on parole?', choices=TRINARY, initial='No')
    parole_info = forms.CharField(label='Parole Information if Other', max_length=100)
    criminal_history = forms.CharField(label='Is there any other information regarding your criminal history '
                                             'that we should know about?', max_length=500)
