from django.shortcuts import render
from djgeojson.views import GeoJSONLayerView
from .models import *

# Create your views here.

def home(request):
    return render(request, 'report/map.html')

def map(request):
    return render(request, 'report/map.html')

class sites_geojson(GeoJSONLayerView):
    model = Site
    precision = 4
    geometry_field = 'location'
    properties = ('name', 'last_report')