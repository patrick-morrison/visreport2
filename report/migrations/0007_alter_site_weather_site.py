# Generated by Django 4.0.3 on 2022-04-01 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0006_site_weather_alter_report_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site_weather',
            name='site',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='report.site'),
        ),
    ]
