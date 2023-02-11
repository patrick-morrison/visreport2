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
            siteweather.swell_marginal = request.POST['swell_marginal']
            siteweather.swell_max = request.POST['swell_max']
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

    if time_since_update.total_seconds() > 3*3600:
        update_weather(slug)
        site_weather = get_object_or_404(SiteWeather, slug=slug)

    wind_data = pd.json_normalize(site_weather.weather['forecasts']['wind']['days'], record_path='entries'
    ).rename(columns={"speed": "wind", "direction": "wind_dir", "directionText": "wind_dir_text"})

    swell_data = pd.json_normalize(site_weather.weather['forecasts']['swell']['days'], record_path='entries'
    ).drop(['period', 'direction'], axis=1
    ).rename(columns={"height": "swell", "directionText": "swell_dir_text"})

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
        'angle': pd.to_numeric(45*((weather['wind_dir']/45).apply(np.round)), downcast='integer').replace([360],0),
    })

    wind = pd.merge(
        rounded,
        con, how="left", on=["angle", "wind"]
    ).rename({'score': 'wind_score'}, axis=1)

    def swell_calc(swell, marginal, max):
        if swell <= marginal:
            score = 0
        elif swell <= max:
            score = 1
        else:
            score = 2
        return score

    swell = weather['swell'].apply(swell_calc, marginal=site_weather.swell_marginal, max = site_weather.swell_max)

    def week_describe(when):
        def time_of_day(dt):
            hour = dt.hour
            day = when.strftime('%A')
            if 6 <= hour < 11:
                return f"{day} morning"
            elif 12 <= hour < 13:
                return f"{day} lunchtime"
            elif 14 <= hour < 16:
                return f"{day} afternoon"
            elif 17 <= hour < 20:
                return f"{day} evening"
            else:
                return "NA"

        when = datetime.strptime(when, "%Y-%m-%d %H:%M:%S")
        time = time_of_day(when)

        return time

    weekday = weather['dateTime'].apply(week_describe)

    def cap(n):
        return min(n, 2)

    scores = pd.DataFrame({
        'time': weather['dateTime'],
        'swell': weather['swell'],
        'weekday' : weekday,
        'swell_dir_text' : weather['swell_dir_text'],
        'wind': (weather['wind']*0.54).round(decimals = 1),
        'wind_dir': weather['wind_dir'],
        'wind_dir_text' : weather['wind_dir_text'],
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

    weather_json = forecast.json()

    if not weather_json['forecasts']['swell']:
        close_url = f'https://api.willyweather.com.au/v2/{api_key}/search/closest.json'
        close = requests.get(
        close_url,
        params={
            'id':id,
            'weatherTypes':"swell",
            "distance": "km"
        },
        )

        # Do something with response data.
        id = close.json()['swell'][0]['id']
        name = close.json()['swell'][0]['name']

        forecast_url = f'https://api.willyweather.com.au/v2/{api_key}/locations/{id}/weather.json'
        startDate = arrow.now().floor('day').format('YYYY-MM-DD')

        forecast = requests.get(
        forecast_url,
        params={
            'forecasts': 'wind,swell',
            'days': 7,
            'startDate': startDate,  # Convert to UTC timestamp
        },
        )
        weather_json = forecast.json()

    # Do something with response data.
    site_weather.weather = weather_json
    site_weather.weather_station = f'Station {id}: {name}'
    site_weather.weather_updated = timezone.now()
    site_weather.save()
