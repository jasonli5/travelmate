from django import forms
from django.forms import ModelForm
from .models import Trip, inputTrip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['destination', 'start_date', 'end_date', 'notes']

class InputForm(ModelForm):
    class Meta:
        model = inputTrip
        fields = ['destination', 'start_date','end_date','activities']

