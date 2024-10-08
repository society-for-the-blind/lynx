# Generated by Django 4.2 on 2024-01-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0087_contact_sip1854_client_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalintake',
            name='age_group',
            field=models.CharField(blank=True, choices=[('younger than 18', 'younger than 18'), ('18-24', '18-24'), ('25-34', '25-34'), ('35-44', '35-44'), ('45-54', '45-54'), ('55-64', '55-64'), ('65-74', '65-74'), ('75-84', '75-84'), ('85 and older', '85 and older')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalintake',
            name='degree',
            field=models.CharField(blank=True, choices=[('Totally Blind', 'Totally Blind'), ('Legally Blind', 'Legally Blind'), ('Severe Vision Impairment', 'Severe Vision Impairment')], max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicalintake',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('American Indian or Alaska Native', 'American Indian or Alaska Native'), ('Asian', 'Asian'), ('Black or African American', 'Black or African American'), ('Native Hawaiian or Pacific Islander', 'Native Hawaiian or Pacific Islander'), ('White', 'White'), ('Did not self identify Race', 'Did not self identify Race'), ('Two or More Races', 'Two or More Races')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalintake',
            name='other_ethnicity',
            field=models.CharField(blank=True, choices=[('Hispanic or Latino', 'Hispanic or Latino')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalintake',
            name='residence_type',
            field=models.CharField(blank=True, choices=[('Private Residence', 'Private Residence'), ('Assisted Living Facility', 'Assisted Living Facility'), ('Nursing Home', 'Nursing Home'), ('Senior Independent Living', 'Senior Independent Living'), ('Homeless', 'Homeless')], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='age_group',
            field=models.CharField(blank=True, choices=[('younger than 18', 'younger than 18'), ('18-24', '18-24'), ('25-34', '25-34'), ('35-44', '35-44'), ('45-54', '45-54'), ('55-64', '55-64'), ('65-74', '65-74'), ('75-84', '75-84'), ('85 and older', '85 and older')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='degree',
            field=models.CharField(blank=True, choices=[('Totally Blind', 'Totally Blind'), ('Legally Blind', 'Legally Blind'), ('Severe Vision Impairment', 'Severe Vision Impairment')], max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('American Indian or Alaska Native', 'American Indian or Alaska Native'), ('Asian', 'Asian'), ('Black or African American', 'Black or African American'), ('Native Hawaiian or Pacific Islander', 'Native Hawaiian or Pacific Islander'), ('White', 'White'), ('Did not self identify Race', 'Did not self identify Race'), ('Two or More Races', 'Two or More Races')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='other_ethnicity',
            field=models.CharField(blank=True, choices=[('Hispanic or Latino', 'Hispanic or Latino')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='residence_type',
            field=models.CharField(blank=True, choices=[('Private Residence', 'Private Residence'), ('Assisted Living Facility', 'Assisted Living Facility'), ('Nursing Home', 'Nursing Home'), ('Senior Independent Living', 'Senior Independent Living'), ('Homeless', 'Homeless')], max_length=150, null=True),
        ),
    ]
