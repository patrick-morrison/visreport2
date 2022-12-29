from django.shortcuts import get_object_or_404, render, redirect
from djgeojson.views import GeoJSONLayerView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import FormMixin
from .models import *
from report.models import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import contextily as cx
import geopandas
import numpy as np
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# Create your views here.

def home(request):
    return render(request, 'report/map.html')

def about(request):
    return render(request, 'report/about.html')

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
            return redirect('detail_site', self.site.slug)


class list_reports(generic.ListView):
    model = Report
    template_name = "report/list_reports.html"


class delete_report(generic.DeleteView):
    model = Report
    def get_success_url(self):
        return reverse_lazy('detail_site', kwargs={'slug': self.object.site.slug})

class sites_display_geojson(GeoJSONLayerView):
    model = Site
    precision = 4
    geometry_field = 'location'
    properties = ('name', 'last_report')

class sites_json(GeoJSONLayerView):
    model = Site
    precision = 4
    geometry_field = 'location'
    properties = ('name', 'slug', 'description','date_added','region1','region2')

def reports_json(request):
   data=list(Report.objects.values())
   return JsonResponse(data,safe=False)

def site_image(request, slug):

    site_code = slug.upper()
    data_url = "https://vis.report/sites_display.geojson"
    sites = geopandas.read_file(data_url)
    reports = pandas.json_normalize(sites['last_report'])
    reports["alpha"] = np.where(reports.recent == 'True', 1, 0.2)
    reports["rank"] = pandas.cut(reports.visibility, [0, 3.1, 8.1, 15.1, 25], right=False, labels=['<3m', '3-8m','8-15m', '15+']).values.add_categories('None')
    reports["rank"] = reports["rank"].fillna('None')


    colors = {'<3m':'#d9534f', '3-8m':'#f0ad4e', '8-15m':'#5cb85c', '15+':'#0275d8', 'None':'#868e96'}

    site = sites.set_index('id', append=True, drop=False).xs(site_code, level=1).reset_index(drop=True)
    xlim = ([site.buffer(0.1).total_bounds[0]-.04,  site.buffer(0.1).total_bounds[2]+.04])
    ylim = ([site.buffer(0.1).total_bounds[1]-.04,  site.buffer(0.1).total_bounds[3]+.04])

    ax = sites.plot(c=reports['rank'].map(colors), alpha = reports.alpha, markersize =250, figsize=(5, 5))

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_axis_off()

    for i, (x, y) in enumerate(zip(sites.geometry.x, sites.geometry.y), start=0):
        ax.annotate(str(sites['id'][i]), (x,y), xytext=(0,0),fontsize=7, textcoords='offset points',
        ha='center', va='center', style='italic',weight='bold', color='white')
        
    t = ax.text(
    site.geometry.x, site.geometry.y+.08,
    f'{site["name"][0]}\n{site["last_report"][0]["since"]}\n{site["last_report"][0]["visibility"]}m reported by @{site["last_report"][0]["username"]}',
    ha="center", va="center", size=12, color='white',
    bbox=dict(boxstyle="round", fc="#292b2c"))

    cx.add_basemap(ax,source=cx.providers.CartoDB.Voyager, crs=sites.crs.to_string(), attribution_size=3)

    response = HttpResponse(content_type ="image/png")
    plt.savefig(response, format="png", pad_inches=0, bbox_inches='tight')
    return response

#User views
class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = "registration/signup.html"

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get(
            'username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view

def account(request):
    form = PreferencesForm
    user = get_object_or_404(User, pk=request.user.pk)
    reports = Report.objects.all().filter(user=user)
    if request.method == 'POST':
        filled_form = PreferencesForm(request.POST, instance=user)
        if filled_form.is_valid():
            filled_form.save()
            return redirect('account')
    return render(request, 'registration/account.html',
     {'user': request.user,
     'reports' : reports,
     'form' : form(initial={'email': user.email,
     'username':user.username},)
    })

