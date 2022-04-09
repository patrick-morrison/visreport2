from email.policy import default
from django.db import models
from report.models import Site
from datetime import datetime, timedelta

def wind_default():
    return """label,angle,wind,score
,0,0,0
,45,0,0
,90,0,0
,135,0,0
,180,0,0
,225,0,0
,270,0,0
,315,0,0
,0,5,0
10kn,45,5,0
,90,5,0
,135,5,0
,180,5,0
,225,5,0
,270,5,0
,315,5,0
,0,10,1
15kn,45,10,0
,90,10,0
,135,10,0
,180,10,1
,225,10,1
,270,10,1
,315,10,1
N,0,15,2
,45,15,0
E,90,15,0
,135,15,0
S,180,15,2
,225,15,2
W,270,15,2
,315,15,2"""
    
def yesterday():
    return datetime.now() - timedelta(1)

# Create your models here.
class SiteWeather(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, primary_key=True)
    slug = models.SlugField(unique=True)
    last_updated = models.DateField(default=datetime.today)
    wind = models.TextField(blank=True,null=True, default=wind_default)
    weather = models.JSONField(blank=True, null=True)
    weather_updated = models.DateTimeField(default=yesterday)
    swell_marginal = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, default = 1.3)
    swell_max = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, default = 2.5)
    weather_station = models.CharField(max_length = 255,blank=True,null=True)

    def __str__(self):
        return self.site.name + " weather"