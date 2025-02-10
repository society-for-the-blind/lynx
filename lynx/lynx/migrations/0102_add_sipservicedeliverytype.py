# Generated by Django 4.2 on 2025-01-12 00:00

from django.db import migrations, models

# NOTE "service delivery type" === "plan type"
#      ----------------------------------------------------
#      On the front-end, this is called  "plan  type",  for
#      historical and  beurocratic  reasons.  Beaurocratic:
#      DOR wants lots of plans, and  having  one  plan  per
#      year per client per service  delivery  type  is  the
#      sweet spot. Historical: the original  implementation
#      is flawed, and every user now  thinks  of  these  as
#      "plan types". Damage done.

# https://wiki.postgresql.org/wiki/CTEReadme
def add_initial_delivery_types(apps, schema_editor):
    SipServiceDeliveryType = apps.get_model('lynx', 'SipServiceDeliveryType')
    SipServiceDeliveryType.objects.bulk_create([
        SipServiceDeliveryType(id=0, parent_id=None, name='ROOT'),
        SipServiceDeliveryType(id=1, parent_id=0, name='in-home'),
        SipServiceDeliveryType(id=2, parent_id=0, name='support group'),
        SipServiceDeliveryType(id=3, parent_id=0, name='training seminar'),
        SipServiceDeliveryType(id=4, parent_id=0, name='community integration'),
        SipServiceDeliveryType(id=5, parent_id=0, name='retreat'),
        SipServiceDeliveryType(id=6, parent_id=2, name='Spanish Support Group'),
        SipServiceDeliveryType(id=7, parent_id=2, name='Asian Support Group'),
        SipServiceDeliveryType(id=8, parent_id=2, name='BASS'),
        SipServiceDeliveryType(id=9, parent_id=0, name='one-time event'),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0101_delete_unused_tables'),
    ]

    operations = [
        migrations.CreateModel(
            name='SipServiceDeliveryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(add_initial_delivery_types),
    ]
