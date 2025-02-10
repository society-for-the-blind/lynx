from django.db import migrations, models


# https://wiki.postgresql.org/wiki/CTEReadme
def add_initial_programs(apps, schema_editor):
    SipProgram = apps.get_model('lynx', 'SipProgram')
    SipProgram.objects.bulk_create([
        SipProgram(id=0, name='SIP', long_name='Senior Impact Program'),
        SipProgram(id=1, name='ILP', long_name='Independent Living Program'),
        SipProgram(id=2, name='Careers Plus', long_name='Careers Plus'),
        SipProgram(id=3, name='Core', long_name='Core Skills Program'),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0103_add_sipserviceevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='SipProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('long_name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(add_initial_programs),
    ]
