# Generated by Django 2.2.17 on 2021-01-05 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0057_auto_20210104_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sipplan',
            name='plan_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]