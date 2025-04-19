from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from .api_utils import get_ai_activity_suggestions, get_ai_additional_info


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SuggestActivitiesAPI(View):
    def post(self, request):
        location = request.POST.get("location")
        already_added = request.POST.get("already_added")
        if already_added:
            already_added = already_added.split(",")
        else:
            already_added = []

        if not location:
            return JsonResponse({"error": "Please provide a location."}, status=400)

        activities = get_ai_activity_suggestions(location, already_added)

        if activities is None:
            return JsonResponse({"error": "Error fetching AI suggestions."}, status=500)

        return JsonResponse({"location": location, "activities": activities}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AdditionalInfoAPI(View):
    def post(self, request):
        location = request.POST.get("location")

        if not location:
            return JsonResponse({"error": "Please provide a location."}, status=400)

        info = get_ai_additional_info(location)

        if info is None:
            return JsonResponse({"error": "Error fetching additional info."}, status=500)

        return JsonResponse({"location": location, "info": info}, status=200)
