# forms.py
from django import forms
from .models import Station

class BookingForm(forms.Form):
    start_station = forms.ModelChoiceField(queryset=Station.objects.all(), label='Starting Station')
    end_station = forms.ModelChoiceField(queryset=Station.objects.all(), label='Ending Station')
    distance = forms.DecimalField(widget=forms.HiddenInput(), required=False, decimal_places=2)