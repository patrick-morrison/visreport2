from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from weather.models import SiteWeather
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import *

class RegionResource(resources.ModelResource):

    class Meta:
        model = Region
        import_id_fields = ('slug', )

class RegionAdmin(ImportExportModelAdmin):
    resource_class = RegionResource

admin.site.register(Region, RegionAdmin)

class SiteResource(resources.ModelResource):

    class Meta:
        model = Site
        import_id_fields = ('slug', )

class WeatherInline(admin.StackedInline):
    model = SiteWeather
    extra = 0

class SiteAdmin(ImportExportModelAdmin):
    list_display = ('slug', 'name', 'date_added', 'nreports')
    inlines = [WeatherInline]
    resource_class = SiteResource

admin.site.register(Site, SiteAdmin)

class ReportResource(resources.ModelResource):

    class Meta:
        model = Report

class ReportAdmin(ImportExportModelAdmin):
    list_display = ('date', 'site', 'visibility', 'user')
    resource_class = ReportResource

admin.site.register(Report, ReportAdmin)

class UserResource(resources.ModelResource):
    class Meta:
        model = User

class UserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = UserResource
    list_display = ('username', 'last_login', 'date_joined')
    pass

admin.site.unregister(User)
admin.site.register(User, UserAdmin)