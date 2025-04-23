from django import forms
from .models import inputTrip

class TripForm(forms.ModelForm):
    class Meta:
        model = inputTrip
        exclude = ['weather']  # Add this to exclude weather from form processing
        fields = ['destination', 'start_date', 'end_date',
                  'weather', 'packing_list', 'activities_list']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
