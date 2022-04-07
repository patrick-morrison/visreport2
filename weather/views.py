from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from .models import *
from report.models import *
import csv
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
import pandas as pd
import numpy as np
import arrow
import requests
import io
from django.conf import settings

# Create your views here.

class site_weather_edit(generic.DetailView):
    model = SiteWeather
    template_name = 'weather/site_weather_edit.html'
    def post(self, request, *args, **kwargs):
            siteweather = get_object_or_404(SiteWeather, slug=self.kwargs['slug'])
            siteweather.wind = request.POST['wind']
            siteweather.last_updated = datetime.today()
            siteweather.save()
            return redirect('siteweather', siteweather.slug)

class site_weather_display(generic.DetailView):
    model = SiteWeather
    template_name = 'weather/site_weather_display.html'
    

def wind_csv(request, slug):
    site_weather = get_object_or_404(SiteWeather, slug=slug)
    
    response = HttpResponse(
        content_type='text/csv',
        content=site_weather.wind,
    )

    return response

def weather_csv(request, slug):
    site_weather = get_object_or_404(SiteWeather, slug=slug)
    time_since_update = timezone.now() - site_weather.weather_updated

    if time_since_update.seconds > 14400:
        update_weather(slug)
        site_weather = get_object_or_404(SiteWeather, slug=slug)

    
    storm = pd.json_normalize(site_weather.weather,record_path =['hours'])
    con = pd.read_csv(io.StringIO(site_weather.wind)).drop('label', axis=1)

    def clamp(n, maxn=15):
        return max(min(maxn, n), 0)
    
    rounded = pd.DataFrame({
        'wind': pd.to_numeric(
            5*((storm['windSpeed.noaa']*1.944/5
        ).apply(np.floor)), downcast='integer'
        ).apply(clamp),
        'angle': pd.to_numeric(45*((storm['windDirection.noaa']/45).apply(np.round)), downcast='integer').replace([360],0),
    })

    wind = pd.merge(
        rounded,
        con, how="left", on=["angle", "wind"]
    ).rename({'score': 'wind_score'}, axis=1)

    def swell_calc(swell, marginal, bad):
        if swell <= marginal:
            score = 0
        elif swell <= bad:
            score = 1
        else:
            score = 2
        return score

    swell = storm['swellHeight.noaa'].apply(swell_calc, marginal=1, bad = 1.2)

    def cap(n):
        return min(n, 2)

    scores = pd.DataFrame({
        'time': storm['time'],
        'swell': storm['swellHeight.noaa'],
        'wind': (storm['windSpeed.noaa']*1.944).round(decimals = 2),
        'wind_dir': storm['windDirection.noaa'],
        'swell_score': swell,
        'wind_score': wind['wind_score'],
        'total_score': (swell+wind['wind_score']).apply(cap),
    })

    csv_file = scores.to_csv()
    
    response = HttpResponse(
        content_type='text/csv',
        content=csv_file,
    )

    return response


def update_weather(slug):
    site_weather = get_object_or_404(SiteWeather, slug=slug)
    # Get first hour of today
    start = arrow.now().floor('day')

    response = requests.get(
    'https://api.stormglass.io/v2/weather/point',
    params={
        'lat': -32.06453,
        'lng': 115.68122863769531,
        'params': ','.join(['swellHeight', 'swellPeriod', 'swellDirection', 'windSpeed', 'windDirection']),
        'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
        'source':'noaa'
    },
    headers={
        'Authorization': settings.STORMGLASS_API
    }
    )

    # Do something with response data.
    storm_json = response.json()
    site_weather.weather = storm_json
    site_weather.weather_updated = timezone.now()
    site_weather.save()
