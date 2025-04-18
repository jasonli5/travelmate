from django import forms
from .models import inputTrip

class TripForm(forms.ModelForm):
    class Meta:
        model = inputTrip
        fields = ['destination', 'start_date', 'end_date', 'activities',
                  'weather', 'packing_list', 'activities_list', 'considerations']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
