# Generated by Django 2.1.5 on 2019-10-06 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0019_authorization_class_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authorization',
            name='class_size',
        ),
        migrations.RemoveField(
            model_name='intake',
            name='preferred_medium',
        ),
        migrations.AddField(
            model_name='address',
            name='preferred_medium',
            field=models.CharField(blank=True, choices=[('N/A', 'N/A'), ('Print', 'Print'), ('Large Print', 'Large Print'), ('Braille', 'Braille'), ('E-Mail', 'E-Mail'), ('Cassette', 'Cassette')], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='degree',
            field=models.CharField(blank=True, choices=[('Stable', 'Stable'), ('Diminishing', 'Diminishing')], max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='income',
            field=models.CharField(blank=True, choices=[('<$12,500', '<$12,500'), ('$12,500-$25,000', '$12,500-$25,000'), ('$25,001-$50,000', '$25,001-$50,000'), ('$50,001-$75,000', '$50,001-$75,000'), ('$75,001-$100,000', '$75,001-$100,000'), ('$100,001-$125,000', '$100,001-$125,000'), ('$125,001-$1150,000', '$125,001-$150,000'), ('>$150,000', '>$150,000')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='living_arrangement',
            field=models.CharField(blank=True, choices=[('Live Alone', 'Live Alone'), ('Live With Spouse', 'Live With Spouse'), ('Live With Other', 'Live With Other'), ('Homeless', 'Homeless')], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='intake',
            name='residence_type',
            field=models.CharField(blank=True, choices=[('Private Residence', 'Private Residence'), ('Community Residential', 'Community Residential'), ('Assisted Living', 'Assisted Living'), ('Skilled Nursing Care', 'Skilled Nursing Care'), ('Homeless', 'Homeless')], max_length=150, null=True),
        ),
    ]