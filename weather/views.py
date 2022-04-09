from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from .models import *
from report.models import *
import csv, json
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
import pandas as pd
import numpy as np
import arrow
import requests
import io
from django.conf import settings
from djgeojson.fields import PointField

# Create your views here.

class site_weather_edit(generic.DetailView):
    model = SiteWeather
    template_name = 'weather/site_weather_edit.html'
    def post(self, request, *args, **kwargs):
            siteweather = get_object_or_404(SiteWeather, slug=self.kwargs['slug'])
            siteweather.wind = request.POST['wind']
            siteweather.last_updated = datetime.today()
            siteweather.save()
            return redirect('siteweatheredit', siteweather.slug)

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
    con = pd.read_csv(io.StringIO(site_weather.wind)).drop('label', axis=1)
    time_since_update = timezone.now() - site_weather.weather_updated

    if time_since_update.total_seconds() > 10:
        update_weather(slug)
        site_weather = get_object_or_404(SiteWeather, slug=slug)

    wind_data = pd.json_normalize(site_weather.weather['forecasts']['wind']['days'], record_path='entries'
    ).drop(['directionText'], axis=1).rename(columns={"speed": "wind", "direction": "wind_dir",})

    swell_data = pd.json_normalize(site_weather.weather['forecasts']['swell']['days'], record_path='entries').drop(['directionText', 'period', 'direction'], axis=1
    ).rename(columns={"height": "swell"})

    weather = pd.merge(
    wind_data,
     swell_data, how="left", on=['dateTime']
     ).fillna(method="ffill")

    def clamp(n, maxn=15):
        return max(min(maxn, n), 0)
    
    rounded = pd.DataFrame({
        'wind': pd.to_numeric(
            5*((weather['wind']*0.54/5
        ).apply(np.floor)), downcast='integer'
        ).apply(clamp),
        'angle': pd.to_numeric(45*((weather['wind']/45).apply(np.round)), downcast='integer').replace([360],0),
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

    swell = weather['swell'].apply(swell_calc, marginal=1, bad = 1.2)

    def cap(n):
        return min(n, 2)

    scores = pd.DataFrame({
        'time': weather['dateTime'],
        'swell': weather['swell'],
        'wind': (weather['wind']*0.54).round(decimals = 2),
        'wind_dir': weather['wind_dir'],
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
    site = get_object_or_404(Site, pk=site_weather.site.slug)

    api_key = settings.WEATHER_API

    lon = site.location['coordinates'][0]
    lat = site.location['coordinates'][1]
    

    search_url = f'https://api.willyweather.com.au/v2/{api_key}/search.json'
    search = requests.get(
        search_url,params={
            'lat': lat,
            'lng': lon,
            "range": 20,
            "distance": "km"
        },
        )
    id = search.json()['location']['id']
    name = search.json()['location']['name']

    forecast_url = f'https://api.willyweather.com.au/v2/{api_key}/locations/{id}/weather.json'
    startDate = arrow.now().floor('day').format('YYYY-MM-DD')
    forecast = requests.get(
    forecast_url,
    params={
        'forecasts': 'wind,swell',
        'days':7,
        'startDate': startDate,  # Convert to UTC timestamp
    },
    )

    # Do something with response data.
    weather_json = forecast.json()
    site_weather.weather = weather_json
    site_weather.weather_station = f'Station {id}: {name}'
    site_weather.weather_updated = timezone.now()
    site_weather.save()
