# Generated by Django 4.2 on 2024-05-14 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0097_assignment_priority_historicalassignment_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsip1854assignment',
            name='priority',
            field=models.CharField(blank=True, choices=[('New', 'New'), ('Returning', 'Returning')], default='New', max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='sip1854assignment',
            name='priority',
            field=models.CharField(blank=True, choices=[('New', 'New'), ('Returning', 'Returning')], default='New', max_length=25, null=True),
        ),
    ]
