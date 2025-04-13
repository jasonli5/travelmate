from django.forms import ModelForm
from django import forms
from .models import inputTrip

class InputForm(ModelForm):
    class Meta:
        model = inputTrip
        fields = ['destination', 'start_date','end_date','activities']