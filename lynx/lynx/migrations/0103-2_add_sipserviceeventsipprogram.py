from django.db import migrations, models
import django.db.models.deletion

# Some service events (probably occasional one-time events)
# may have multiple SIP programs associated with them.
class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0103-1_add_sipprogram'),
    ]

    operations = [
        migrations.CreateModel(
            name='SipServiceEventSipProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.sipserviceevent')),
                ('sip_program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.sipprogram')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
