# Generated by Django 4.0.3 on 2022-04-01 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_alter_site_weather_site'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Site_Weather',
            new_name='SiteWeather',
        ),
    ]
