from django.db import migrations, models

# This will probably be unused, but adding it in case
# there is a need.

def add_initial_roles(apps, schema_editor):
    SipServiceEventInstructorRole = apps.get_model('lynx', 'SipServiceEventInstructorRole')
    SipServiceEventInstructorRole.objects.bulk_create([
        SipServiceEventInstructorRole(id=0, name='instructor'),
        SipServiceEventInstructorRole(id=1, name='facilitator'),
        SipServiceEventInstructorRole(id=2, name='switchboard'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0113_add_oiboutcome'),
    ]

    operations = [
        migrations.CreateModel(
            name='SipServiceEventInstructorRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(add_initial_roles),
    ]
