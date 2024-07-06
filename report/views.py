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
from django.utils import timezone


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
        
    def get_queryset(self):
        return Report.objects.exclude(site__region1='newcastle')

class guide(generic.ListView):
    model = Report
    template_name = "report/guide.html"
    def get_queryset(self):
        seven_day_before = timezone.now() - timedelta(days=7)
        recent_reports = Report.objects.filter(date__gte=seven_day_before)
        recent_reports = recent_reports.exclude(site__region1='newcastle')
        return recent_reports


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

