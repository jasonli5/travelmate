from django import forms
from django.contrib.auth.models import User

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

    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form_control'})
    )

class CollabInviteForm(forms.Form):
    email = forms.EmailField(label="Invite Collaborator", required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.user and email == self.user.email:
            raise forms.ValidationError("You cannot invite yourself!")
        return email


