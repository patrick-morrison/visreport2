"""visreport2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from report import views
from weather import views as weather_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('list', views.list_reports.as_view(), name='list'),
    path('guide', views.guide.as_view(), name='guide'),
    path('<slug:slug>', views.detail_site.as_view(), name='detail_site'),
    path('sites.json', views.sites_json.as_view(), name='sites_json'),
    path('reports.json', views.reports_json, name='reports_json'),
    path('reports/delete/<int:pk>', views.delete_report.as_view(), name='delete_report'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sites_display.geojson', views.sites_display_geojson.as_view(), name='sites_display_geojson'),
    path('sites_weather/<slug:slug>', weather_views.site_weather_display.as_view(), name='siteweatherdisplay'),
    path('sites_weather/<slug:slug>/edit/', weather_views.site_weather_edit.as_view(), name='siteweatheredit'),
    path('sites_weather/<slug:slug>/wind_csv/', weather_views.wind_csv, name='wind_csv'),
    path('sites_weather/<slug:slug>/weather_csv/', weather_views.weather_csv, name='weather_csv'),
    # AUTH
    path('accounts/signup', views.SignUp.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('account/', views.account, name='account'),
    # Custom redirect for sealrocks
    path('sealrocks', RedirectView.as_view(url='SLR', permanent=True)),
]

