from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

# Register your models here.
from .models import *

admin.site.register(Region, LeafletGeoAdmin)
admin.site.register(Site, LeafletGeoAdmin)
admin.site.register(Report, LeafletGeoAdmin)