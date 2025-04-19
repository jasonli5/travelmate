from django.shortcuts import render

from ai.models import Activity
from ai.forms import ActivityFormSet
from ai.api_utils import get_ai_additional_info
from .models import inputTrip, travelRecommendations
from django.shortcuts import render, redirect, get_object_or_404
from .models import inputTrip
from packinglist.models import Item
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from django.utils import timezone
from .forms import TripForm


PREDEFINED_TRIPS = {
    'paris': {
        'destination': 'Paris, France',
        'activities': 'Visit Eiffel Tower, Try a baguette, Watch a mime, Cruise the Seine',
        'duration': 7
    },
    'tokyo': {
        'destination': 'Tokyo, Japan',
        'activities': 'Visit Shibuya Crossing, Try sushi, See cherry blossoms, Explore Akihabara',
        'duration': 7
    },
    'new york city': {
        'destination': 'New York City, USA',
        'activities': 'See Times Square, Visit Statue of Liberty, Walk in Central Park, See a Broadway show',
        'duration': 7
    },
    'barcelona': {
        'destination': 'Barcelona, Spain',
        'activities': 'Visit Sagrada Familia, Walk Las Ramblas, Try paella, Explore Park Güell',
        'duration': 7
    },
    'maui': {
        'destination': 'Maui, Hawaii',
        'activities': 'Road to Hana, Snorkel at Molokini, Watch sunrise at Haleakalā, Attend a luau',
        'duration': 7
    },
    'aspen': {
        'destination': 'Aspen, Colorado',
        'activities': 'Skiing/snowboarding, Visit Maroon Bells, Explore downtown Aspen, Relax at hot springs',
        'duration': 7
    }
}
# Create your views here.
def trip_draft(request):
    template_data= {}
    template_data['title'] = 'Editing New Trip'
    trip = inputTrip.objects.filter(user=request.user).first()
    template_data['destination'] = trip.destination
    template_data['dates'] = str(trip.start_date) + " - " + str(trip.end_date)
    template_data['activities'] = trip.activites.split(",")
    return render(request, 'trips/edit_trip.html', {'template_data' : template_data})
def edit_trip(request):
    template_data= {}
    template_data['title'] = 'Editing New Trip'
    trip = inputTrip.objects.filter(user=request.user).first()

    template_data['destination'] = trip.destination
    template_data['dates'] = str(trip.start_date) + " - " + str(trip.end_date)
    template_data['activities'] = trip.activites.split(",")

    return render(request, 'trips/edit_trip.html', {'template_data' : template_data})

def travel_recs(request):
    recs = travelRecommendations.objects.all()
    return render(request, 'travelrecs/recs.html', {'recs': recs})

@login_required
def add_travel_recs(request):
    # Get and clean the destination parameter
    dest_key = request.GET.get('destination', '').strip().lower()

    # Check if it's one of our predefined destinations
    if dest_key in PREDEFINED_TRIPS:
        trip_data = PREDEFINED_TRIPS[dest_key]
        try:
            # Calculate dates
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=trip_data['duration'])

            # Create the trip
            new_trip = inputTrip(
                user=request.user if request.user.is_authenticated else None,
                destination=trip_data['destination'],
                start_date=start_date,
                end_date=end_date,
            )

            # Generate additional info using AI
            info = get_ai_additional_info(new_trip.destination)
            if info:
                new_trip.considerations = info

            new_trip.save()

            if trip_data['activities']:
                for activity in trip_data['activities'].split(','):
                    new_activity = Activity(
                        name=activity.strip(),
                        trip=new_trip,
                    )
                    new_activity.save()
            return redirect('edit_trip', trip_id=new_trip.id)  # Redirect to the trips list page

        except Exception as e:
            messages.error(request, f'Error creating trip: {str(e)}')
            return redirect('home.index')

    # If no matching destination found, proceed normally
    return render(request, 'home.index', {'destination': dest_key})

@login_required  # Ensures only logged-in users can access this
def plan_trip(request):
    if request.method == 'POST':
        try:
            # Create and save the new trip
            new_trip = inputTrip(
                user=request.user,  # Automatically associate with logged-in user
                destination=request.POST['destination'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                # activities=request.POST['activities']
            )

            # Generate additional info using AI
            info = get_ai_additional_info(new_trip.destination)

            if info:
                new_trip.considerations = info

            new_trip.save() # Save trip first

            if request.POST['activities']:
                parsed_activities = request.POST['activities'].split(',')
                for activity in parsed_activities:
                    new_activity = Activity(
                        name=activity.strip(),
                        trip=new_trip,
                        is_ai_suggested=False
                    )
                    new_activity.save()
            
            return redirect('edit_trip', trip_id=new_trip.id)  # Redirect to the edit page of the newly created trip

        except Exception as e:
            messages.error(request, f'Error saving your trip: {str(e)}')

    destination = request.GET.get('destination', '')
    # If GET request or if there was an error, render the form page
    return render(request, 'home/index.html', {'destination': destination, 'today': date.today().isoformat()})
@login_required
def trips_list(request):
    trips = inputTrip.objects.filter(user=request.user)
    return render(request, 'trips/list.html', {'trips': trips})
def delete_trip(request, trip_id):
    if request.method == 'POST':
        trip = get_object_or_404(inputTrip, id=trip_id, user=request.user)
        trip.delete()
        return redirect('trips')  # redirect to your trips listing page
    else:
        # If someone tries to access this URL directly via GET, redirect them
        return redirect('trips')

@login_required
def edit_trip(request, trip_id):
    trip = get_object_or_404(inputTrip, id=trip_id, user=request.user)
    all_items = Item.objects.filter(trip=trip_id)  # Add this line
    items = all_items.filter(is_ai_suggested=False).order_by("id")
    ai_items = all_items.filter(is_ai_suggested=True).order_by("id")
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        activity_formset = ActivityFormSet(request.POST, instance=trip)

        if form.is_valid() and activity_formset.is_valid():
            form.save()
            activity_formset.save()
            messages.success(request, 'Trip updated successfully!')
            return redirect('trips')  # adjust this to match your trip list url name
    else:
        form = TripForm(instance=trip)
        activity_formset = ActivityFormSet(instance=trip)
    

    return render(request, 'trips/edit_trip.html', {'form': form, 'trip': trip, 'items': items, "ai_items" : ai_items})

    return render(request, 'trips/edit_trip.html', {'form': form, 'trip': trip, 'activity_formset': activity_formset})

