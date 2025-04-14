from django.shortcuts import render,redirect, get_object_or_404
from trips.forms import InputForm
from trips.models import inputTrip
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})


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
            return redirect('trips')  # Redirect to a trips listing page

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