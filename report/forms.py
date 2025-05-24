from .models import  Report
from django import forms
from datetime import datetime, timedelta, time
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import ReCaptchaField


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", 'captcha')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class DateSelectorWidget(forms.MultiWidget):
    def past_week(self):
        today = datetime.now()
        days = []
        for i in range(7):  # Today + 6 days back
            day_date = today - timedelta(days=i)
            if i == 0:
                label = 'Today'
            elif i == 1:
                label = f'Yesterday {day_date.strftime("%b %d")}'
            else:
                label = f'{day_date.strftime("%A %b %d")}'
            days.append((day_date.strftime('%Y-%m-%d'), label))
        return days

    def __init__(self, attrs=None):
        timeofday = [(time(i).strftime('%H'), time(i).strftime('%I %p')) for i in range(24)]
        widgets = [
            forms.Select(attrs=attrs, choices=[]),
            forms.Select(attrs=attrs, choices=timeofday),
        ]
        super().__init__(widgets, attrs)

    def get_context(self, name, value, attrs):
        # Ensure choices are current before rendering
        self.widgets[0].choices = self.past_week()
        context = super().get_context(name, value, attrs)
        return context

    def decompress(self, value):
        if isinstance(value, datetime):
            return [value.day, value.timeofday]
        elif isinstance(value, str):
            day, timeofday = value.split(' ')
            return [day, timeofday]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        day, timeofday = super().value_from_datadict(data, files, name)
        return '{} {}:00'.format(day, timeofday)

    def subwidgets(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        return context['widget']['subwidgets']

class DateSelectorWidgetMobile(DateSelectorWidget):
    template_name = 'widgets/daywidgetmobile.html'

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['date', 'conditions', 'visibility', 'comments']
        widgets = {
            'date': DateSelectorWidgetMobile,
            'visibility': forms.NumberInput(attrs={'placeholder': '0-25m', 'min':0,'max':25}),
            'comments': forms.TextInput(attrs={'placeholder': 'Optional'})
        }
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        def hour_ago():
            return (datetime.now() - timedelta(hours = 1)).strftime('%H')

        def today():
            return datetime.strftime(datetime.now() - timedelta(hours = 1), '%Y-%m-%d')


        self.fields['date'].initial = [today(), hour_ago()]

class PreferencesForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']