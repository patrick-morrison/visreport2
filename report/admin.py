from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Region)
admin.site.register(Site)
admin.site.register(Report)