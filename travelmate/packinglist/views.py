from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, inputTrip  # Make sure to import inputTrip
from django.views.decorators.http import require_POST
from .api_utils import get_ai_suggestions
from ai.models import Activity
from ai.forms import ActivityFormSet
from ai.api_utils import get_ai_additional_info
from django.core.exceptions import PermissionDenied



def get_trip_and_check_permission(request, trip_id):
    trip = get_object_or_404(inputTrip, pk=trip_id)
    if request.user not in trip.collaborators.all() and request.user != trip.user:
        raise PermissionDenied("You don't have permission to access this trip")
    return trip

@login_required
def create_item(request):
    if request.method == "POST":
        # Handle adding existing AI item
        if "existing_item_id" in request.POST:
            item = get_object_or_404(
                Item, pk=request.POST["existing_item_id"]
            )
            item.is_ai_suggested = False
            item.save()
            return JsonResponse({"status": "success"})

        # Handle new item creation
        if request.POST.get("name") and request.POST.get("description"):
            trip_id = request.POST.get("trip_id")
            if trip_id:
                trip = get_object_or_404(inputTrip, pk=trip_id)
                item = Item(
                    name=request.POST["name"],
                    description=request.POST["description"],
                    user=trip.user,
                    is_ai_suggested=request.POST.get("is_ai_suggested", False),
                    trip_id=trip_id
                )
            item.save()
            return redirect("edit_trip", trip_id=request.POST.get("trip_id"))

    return redirect("edit_trip")


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    trip = get_trip_and_check_permission(request, item.trip_id)

    if request.method == "POST":
        item.name = request.POST.get("name", item.name)
        item.description = request.POST.get("description", item.description)
        item.save()

        # Redirect back to packing list with trip context
        return redirect("edit_trip", trip_id=item.trip_id)

    return redirect("edit_trip")


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    trip = get_trip_and_check_permission(request, item.trip_id)

    trip_id = item.trip_id  # Save trip_id before deletion

    if request.method == "POST":
        item.delete()

    # Redirect back to the appropriate packing list
    return redirect("edit_trip", trip_id=trip_id if trip_id else None)


@login_required
def ai_suggest_items(request):
    if request.method == "POST":
        location = request.POST.get("location")
        count = int(request.POST.get("count", 6))
        trip_id = request.POST.get("trip_id")  # Get trip_id from request
        start_date = end_date = None;
        activities = [];
        considerations = "";

        if trip_id:
            trip = inputTrip.objects.get(id=trip_id)
            start_date = trip.start_date
            end_date = trip.end_date
            activities = Activity.objects.filter(trip=trip).values_list('name', flat=True)
            activities = list(activities)  # Convert to list
            considerations = trip.considerations

        request.session["last_location"] = location
        existing_items = list(
            Item.objects.filter(user=request.user, trip_id=trip_id).values("name", "description")
        )

        # Debugging output
        print("\n=== DEBUGGING LOCATION DATA ===")
        print(f"Raw POST data: {request.POST}")
        print(f"Destination from form: {location}")
        print(f"Found trip: {trip.destination} ({start_date} to {end_date})")
        print(f"Activities are: {activities}")
        print(f"Considerations are: {considerations}")


        if trip_id:
            try:
                print(f"Trip destination from DB: {trip.destination}")
            except inputTrip.DoesNotExist:
                print("Trip not found in database")

        suggestions = get_ai_suggestions(location, start_date, end_date, count, existing_items, activities, considerations)
        suggestions["trip_id"] = trip_id  # Include trip_id in response
        return JsonResponse(suggestions)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def create_ai_item(request):
    if request.method == "POST":
        item = Item(
            name=request.POST.get("title"),
            description=request.POST.get("description"),
            user=request.user,
            is_ai_suggested=True,
            trip_id=request.POST.get("trip_id")  # Add trip association
        )
        item.save()
        return redirect("edit_trip", trip_id=request.POST.get("trip_id"))

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def packing_list(request, trip_id=None):
    # Get base queryset
    items_query = Item.objects.filter(user=request.user)
    trip = None

    # If trip_id is provided, filter by trip
    if trip_id:
        trip = get_object_or_404(inputTrip, id=trip_id, user=request.user)
        items_query = items_query.filter(trip=trip)

    # Separate AI and user items
    user_items = items_query.filter(is_ai_suggested=False).order_by("id")
    ai_items = items_query.filter(is_ai_suggested=True).order_by("id")
    context = {
        "items": user_items,
        "ai_items": ai_items,
        "trip": trip,
        "default_location": request.session.get("last_location", ""),
        "all_trips": inputTrip.objects.filter(user=request.user)  # For trip selection
    }

    return render(request, "packinglist/packing_list.html", context)