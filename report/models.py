from django.db import models
from djgeojson.fields import PointField, PolygonField
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms.models import model_to_dict
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime

# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(primary_key=True)
    location = PolygonField()
    date_added = models.DateField()
    
    def __str__(self):
        return self.name

class Site(models.Model):
    slug = models.SlugField(max_length=3, default='xxx', primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=225, null=True, blank=True)
    location = PointField()
    date_added = models.DateField()
    region1 = models.ForeignKey(Region, on_delete=models.CASCADE)
    region2 = models.CharField(max_length=50, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    link_caption = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name + " (" + self.slug + ")"

    @property
    def last_report(self):
        try:
            report = model_to_dict(Report.objects.filter(site=self.pk).latest('date'))
            report.update({'recent': str(((timezone.now() - report['date']).days)<7)})
            report.update({'since': str(naturaltime(report['date']))})
            return report
        except:
            return {'recent' : 'None'}




class Report(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date = models.DateTimeField()
    conditions = models.CharField(max_length=225)
    visibility = models.IntegerField(validators=[
            MaxValueValidator(25),
            MinValueValidator(0)
        ])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return str(self.date.strftime("%Y-%m-%d-%H")) +"_"+ self.site.slug + "_by_"+ self.user.username