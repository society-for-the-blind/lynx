# Generated by Django 4.2 on 2023-10-01 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import lynx.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lynx', '0082_alter_historicaladdress_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sip1854Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_date', models.DateField(auto_now_add=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('assignment_status', models.CharField(blank=True, choices=[('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Assigned', max_length=25, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lynx.contact')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sip1854instructors', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.SET(lynx.models.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
