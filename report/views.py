from django.shortcuts import get_object_or_404, render, redirect
from djgeojson.views import GeoJSONLayerView
from django.views import generic
from django.views.generic.edit import FormMixin
from .models import *
from .forms import *


# Create your views here.

def home(request):
    return render(request, 'report/map.html')

def map(request):
    return render(request, 'report/map.html')

class detail_site(FormMixin, generic.DetailView):
    model = Site
    form_class = ReportForm
    template_name = 'report/detail_site.html'
    def post(self, request, *args, **kwargs):
        filled_form = ReportForm(request.POST)
        if filled_form.is_valid():
            report = Report()
            report.date = filled_form.cleaned_data['date']
            self.site = get_object_or_404(Site, slug=self.kwargs['slug'])
            report.site = self.site
            report.conditions = filled_form.cleaned_data['conditions']
            report.comments = filled_form.cleaned_data['comments']
            report.visibility = filled_form.cleaned_data['visibility']
            report.user = request.user
            report.save()
            return redirect('map')

class sites_display_geojson(GeoJSONLayerView):
    model = Site
    precision = 4
    geometry_field = 'location'
    properties = ('name', 'last_report')