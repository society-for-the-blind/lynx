from django.db import migrations, models

def add_initial_programs(apps, schema_editor):
    OIBProgram = apps.get_model('lynx', 'OIBProgram')
    OIBProgram.objects.bulk_create([
        OIBProgram(id=0, oib_program='SIP', long_name='Senior Impact Program'),
        OIBProgram(id=1, oib_program='ILP', long_name='Independent Living Program'),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0101_delete_unused_tables'),
    ]

    operations = [
        migrations.CreateModel(
            name='OIBProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oib_program', models.CharField(max_length=255)),
                ('long_name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(add_initial_programs),
    ]
