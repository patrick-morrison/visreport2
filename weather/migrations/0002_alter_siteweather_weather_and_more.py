# Generated by Django 4.0.3 on 2022-04-07 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteweather',
            name='weather',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='siteweather',
            name='weather_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
