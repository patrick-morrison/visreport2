from django.db import models
from report.models import Site

# Create your models here.
class SiteWeather(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, primary_key=True)
    slug = models.SlugField(unique=True)
    last_updated = models.DateField()
    wind = models.TextField(blank=True,null=True)
    weather = models.JSONField(blank=True, null=True)
    weather_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.site.name + " weather"