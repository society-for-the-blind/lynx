from django.db import migrations, models
import django.db.models.deletion

def add_initial_type_choice_pairs(apps, schema_editor):
    def add_pair(oib_outcome_type_id, oib_outcome_choice_id):
        # get models
        OibOutcomeType = apps.get_model('lynx', 'OibOutcomeType')
        OibOutcomeChoice = apps.get_model('lynx', 'OibOutcomeChoice')
        OibOutcomeTypeChoice = apps.get_model('lynx', 'OibOutcomeTypeChoice')
        # get types and choices
        oib_outcome_type = OibOutcomeType.objects.get(id=oib_outcome_type_id)
        oib_outcome_choice = OibOutcomeChoice.objects.get(id=oib_outcome_choice_id)
        # add pairs
        OibOutcomeTypeChoice.objects.create(
            oib_outcome_type=oib_outcome_type,
            oib_outcome_choice=oib_outcome_choice
        )

    add_pair(0, 4) # AT - Not assessed etc.
    add_pair(0, 5)
    add_pair(0, 6)
    add_pair(0, 7)
    add_pair(1, 4) # IL/A - Not assessed etc.
    add_pair(1, 5)
    add_pair(1, 6)
    add_pair(1, 7)
    add_pair(2, 0) # Living Situation - Plan not complete etc.
    add_pair(2, 1)
    add_pair(2, 2)
    add_pair(2, 3)
    add_pair(3, 0) # Home and Community - Plan not complete etc.
    add_pair(3, 1)
    add_pair(3, 2)
    add_pair(3, 3)
    add_pair(4, 8) # Employment - Not Interested etc.
    add_pair(4, 9)
    add_pair(4, 10)
    add_pair(4, 11)

class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0111_add_oiboutcomechoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='OibOutcomeTypeChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oib_outcome_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.OibOutcomeType')),
                ('oib_outcome_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.OibOutcomeChoice')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.RunPython(add_initial_type_choice_pairs),
    ]