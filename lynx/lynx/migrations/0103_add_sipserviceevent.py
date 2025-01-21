# Generated by Django 4.2 on 2025-01-12 00:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0102_add_sipservicedeliverytype'),
    ]

    operations = [
        migrations.CreateModel(
            name='SipServiceEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # NOTE 1 service delivery type per service event
                #      There was  a  many-to-many  relationship  between
                #      service events and service delivery types (see at
                #      the bottom), but because  I  have  never  seen  a
                #      service  event  delivered  by  multiple   service
                #      delivery types,  decided  to  simply  include  it
                #      here.
                ('service_delivery_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.sipservicedeliverytype')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('length', models.DurationField()),
                ('note', models.TextField(blank=True, default="")),
            ],
        ),
    ]

# This migration is excluded, because realized that a service event is delivered on/by one service delivery type only.
# Generated by Django 4.2 on 2025-01-12 00:00

# from django.db import migrations, models
# import django.db.models.deletion


# class Migration(migrations.Migration):

#     dependencies = [
#         ('lynx', '0105_add_sipserviceeventsipservice'),
#     ]

#     operations = [
#         migrations.CreateModel(
#             name='SipServiceEventSipServiceDeliveryType',
#             fields=[
#                 ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('service_delivery_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.sipservicedeliverytype')),
#                 ('service_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.sipserviceevent')),
#             ],
#         ),
#     ]
