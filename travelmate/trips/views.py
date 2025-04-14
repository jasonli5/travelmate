from django.shortcuts import render
from .models import inputTrip
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def edit_trip(request):
    template_data= {}
    template_data['title'] = 'Editing New Trip'
    trip = inputTrip.objects.filter(user=request.user).first()

    template_data['destination'] = trip.destination
    template_data['dates'] = str(trip.start_date) + " - " + str(trip.end_date)
    template_data['activities'] = trip.activites.split(",")

    return render(request, 'trips/edit_trip.html', {'template_data' : template_data})

def travel_recs(request):
    recs = [
        {"name": "New York City", "image": "img/nyc.jpg", "description": "The city that never sleeps, known for Broadway, Central Park, amazing restaurants, Empire State Building, Statue of Liberty, and so much more."},
        {"name": "Tokyo", "image": "img/toyko.jpeg", "description": "A buzzing metropolis known for ancient temples like Senso-ji, fresh sushi markets, cherry blossoms, bullet trains, and lots of shopping and entertainment."},
        {"name": "Paris", "image": "img/paris.jpg", "description": "The city of romance, known for the Eiffel Tower, Louvre Museum, charming cafes, iconic fashion, and of course...croissants."},
        {"name": "Barcelona", "image": "img/barcelona.jpg", "description": "The stunning city filled with markets, beaches, historical locations, and a deep, fascinating history."},
        {"name": "Maui", "image": "img/maui.jpg", "description": "Tropical paradise with stunning beaches, waterfalls, lush rainforests, and incredible sunset views."},
        {"name": "Aspen", "image": "img/aspen.jpg", "description": "The iconic mountain town known for world-class ski resorts, views of the Rocky Mountains, resorts, and a charming downtown scene."},
    ]
    return render(request, 'travelrecs/recs.html', {'recs': recs})
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
                activities=request.POST['activities']
            )
            new_trip.save()
            return redirect('trips')  # Redirect to a trips listing page, will need to change to planning page

        except Exception as e:
            messages.error(request, f'Error saving your trip: {str(e)}')

    # If GET request or if there was an error, render the form page
    return render(request, 'home/index.html')
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

