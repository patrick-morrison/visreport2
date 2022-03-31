from .models import  Report
from django import forms
from datetime import datetime, timedelta, time

class DateSelectorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        today = datetime.strftime(datetime.now(), '%Y-%m-%d')
        yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        day = [(today,'Today'), (yesterday, "Yesterday")]
        timeofday = [(time(i).strftime('%H'), time(i).strftime('%I %p')) for i in range(24)]
        widgets = [
            forms.Select(attrs=attrs, choices=day),
            forms.Select(attrs=attrs, choices=timeofday),
        ]
        super().__init__(widgets, attrs)

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
        self.fields['date'].initial = [datetime.strftime(datetime.now(), '%Y-%m-%d'), (datetime.now() - timedelta(hours = 1)).strftime('%H')]