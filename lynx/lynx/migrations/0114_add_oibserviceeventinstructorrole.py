from django.db import migrations, models

# This will probably be unused, but adding it in case
# there is a need.

def add_initial_roles(apps, schema_editor):
    OIBServiceEventInstructorRole = apps.get_model('lynx', 'OIBServiceEventInstructorRole')
    OIBServiceEventInstructorRole.objects.bulk_create([
        OIBServiceEventInstructorRole(id=0, oib_service_event_instructor_role='instructor'),
        OIBServiceEventInstructorRole(id=1, oib_service_event_instructor_role='facilitator'),
        OIBServiceEventInstructorRole(id=2, oib_service_event_instructor_role='switchboard'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0113_add_oiboutcome'),
    ]

    operations = [
        migrations.CreateModel(
            name='OIBServiceEventInstructorRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oib_service_event_instructor_role', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(add_initial_roles),
    ]
