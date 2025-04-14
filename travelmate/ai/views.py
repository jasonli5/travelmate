from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .api_utils import get_ai_activity_suggestions, get_ai_additional_info


@login_required
def suggest_activities(request):
    if request.method == "POST":
        location = request.POST.get("location")
        # For demonstration, we'll use dummy data
        # Dummy data for demonstration

        if not location:
            return render(request, "ai/activities.html", {"error": "Please provide a location."})

        activities = get_ai_activity_suggestions(location)

        info = get_ai_additional_info(location)

        if activities is None or info is None:
            return render(request, "ai/activities.html", {"error": "Error fetching AI suggestions."})

        return render(request, "ai/activities.html", {"location": location, "activities": activities, "info": info})
    else:
        # If not a POST request, render the initial form
        return render(request, "ai/activities.html")
