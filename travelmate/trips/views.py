from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Trip
from .forms import TripForm

@login_required
def trip_list(request):
    trips = Trip.objects.filter(user=request.user)
    return render(request, 'trips/trip_list.html', {'trips': trips})

@login_required
def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    return render(request, 'trips/trip_detail.html', {'trip': trip})

@login_required
def trip_create(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            return redirect('trip_detail', pk=trip.pk)
    else:
        form = TripForm()
    return render(request, 'trips/trip_form.html', {'form': form})

@login_required
def trip_update(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    form = TripForm(request.POST or None, instance=trip)
    if form.is_valid():
        form.save()
        return redirect('trip_detail', pk=trip.pk)
    return render(request, 'trips/trip_form.html', {'form': form})

@login_required
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    if request.method == 'POST':
        trip.delete()
        return redirect('trip_list')
    return render(request, 'trips/trip_confirm_delete.html', {'trip': trip})
