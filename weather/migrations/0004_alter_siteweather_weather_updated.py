# Generated by Django 4.0.3 on 2022-04-07 15:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0003_alter_siteweather_last_updated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteweather',
            name='weather_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 4, 6, 23, 54, 5, 760505)),
        ),
    ]
