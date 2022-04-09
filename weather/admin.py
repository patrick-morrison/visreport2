from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Register your models here.

class SiteWeatherResource(resources.ModelResource):

    class Meta:
        model = SiteWeather

class SiteWeatherAdmin(ImportExportModelAdmin):
    resource_class = SiteWeatherResource

admin.site.register(SiteWeather, SiteWeatherAdmin)