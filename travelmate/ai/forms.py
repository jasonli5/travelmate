from django.forms import inlineformset_factory

from .models import Activity
from trips.models import inputTrip


ActivityFormSet = inlineformset_factory(
    inputTrip,                      # Parent model
    Activity,                  # Child model
    fields=['name'],  # Fields you want to edit
    extra=0,                   # Number of empty forms to display
    can_delete=True            # Let users remove activities
)