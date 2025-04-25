import smtplib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from ai.models import Activity
from ai.forms import ActivityFormSet
from ai.api_utils import get_ai_additional_info
from django.template.loader import render_to_string

from .models import inputTrip, travelRecommendations
from django.shortcuts import render, redirect, get_object_or_404
from .models import inputTrip
from packinglist.models import Item
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from django.utils import timezone
from .forms import TripForm, CollabInviteForm
from ai.models import Activity
from ai.forms import ActivityFormSet
from ai.api_utils import get_ai_additional_info
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import inputTrip
from weather_data.api_utils import get_coordinates, get_date_range_weather
import json
from .admin import load_predefined_trips




# Create your views here.
def trip_draft(request):
    template_data= {}
    template_data['title'] = 'Editing New Trip'
    trip = inputTrip.objects.filter(user=request.user).first()
    template_data['destination'] = trip.destination
    template_data['dates'] = str(trip.start_date) + " - " + str(trip.end_date)
    template_data['activities'] = trip.activites.split(",")
    return render(request, 'trips/edit_trip.html', {'template_data' : template_data})


@login_required
def edit_trip(request, trip_id):
    trip = get_object_or_404(inputTrip, id=trip_id, user=request.user)
    all_items = Item.objects.filter(trip=trip_id)
    items = all_items.filter(is_ai_suggested=False).order_by("id")
    ai_items = all_items.filter(is_ai_suggested=True).order_by("id")

    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        activity_formset = ActivityFormSet(request.POST, instance=trip)
        collab_form = CollabInviteForm(request.POST, user=request.user)

        if form.is_valid() and activity_formset.is_valid():
            # Save the form without committing to database
            trip = form.save(commit=False)
            # Preserve the existing weather data
            original_trip = inputTrip.objects.get(id=trip_id)
            trip.weather = original_trip.weather
            # Now save to database
            trip.save()

            activity_formset.save()

            # If the collaborator invite form is valid, send the invitation email
            email = collab_form.cleaned_data['email']
            send_mail(
                'Trip Collaboration Invitation',
                f'You have been invited to collaborate on the trip to {trip.destination}. Please log in to accept the invitation.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect('trips')
    else:
        form = TripForm(instance=trip)
        activity_formset = ActivityFormSet(instance=trip)
        collab_form = CollabInviteForm(user=request.user)

    return render(request, 'trips/edit_trip.html', {
        'form': form,
        'trip': trip,
        'activity_formset': activity_formset,
        'items': items,
        "ai_items": ai_items,
        'collab_form': collab_form,
    })

def travel_recs(request):
    recs = travelRecommendations.objects.all()
    return render(request, 'travelrecs/recs.html', {'recs': recs})


@login_required
def add_travel_recs(request):
    # Get and clean the destination parameter
    dest_key = request.GET.get('destination', '').strip().lower()

    # Load trips from JSON file
    predefined_trips = load_predefined_trips()

    # Check if it's one of our predefined destinations
    if dest_key in predefined_trips:
        trip_data = predefined_trips[dest_key]
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
            return redirect('edit_trip', trip_id=new_trip.id)

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
'''
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
            return redirect('trips')  # adjust this to match your trip list url name
    else:
        form = TripForm(instance=trip)
        activity_formset = ActivityFormSet(instance=trip)

    return render(request, 'trips/edit_trip.html', {'form': form, 'trip': trip, 'activity_formset': activity_formset, 'items': items, "ai_items" : ai_items})
'''

def generate_trip_weather(trip_id):
    """
    Generate weather forecast for all dates in a trip and save to the trip model
    """
    # Get the trip object
    trip = get_object_or_404(inputTrip, id=trip_id)

    # Convert dates to datetime objects
    start_date = datetime.combine(trip.start_date, datetime.min.time())
    end_date = datetime.combine(trip.end_date, datetime.min.time())

    try:
        # Get coordinates for the destination
        coords = get_coordinates(trip.destination)
        location_name = coords['name']

        # Get weather for the entire trip duration
        weather_reports = get_date_range_weather(
            coords['lat'],
            coords['lon'],
            location_name,
            start_date,
            end_date
        )

        # Combine all weather reports into a single JSON-serializable structure
        weather_data = {
            'location': location_name,
            'coordinates': {
                'lat': coords['lat'],
                'lon': coords['lon']
            },
            'reports': []
        }

        current_date = start_date
        for report in weather_reports:
            weather_data['reports'].append({
                'date': current_date.strftime('%Y-%m-%d'),
                'report': report.strip()  # Remove extra whitespace
            })
            current_date += timedelta(days=1)

        # Save to the trip model
        trip.weather = json.dumps(weather_data, indent=2)
        trip.save()

        return True, "Weather data generated successfully"

    except Exception as e:
        print(start_date)
        print(end_date)
        return False, f"Error generating weather data: {str(e)}"

@login_required
def generate_weather_view(request, trip_id):
    if request.method == 'POST':
        success, message = generate_trip_weather(trip_id)
        return JsonResponse({'success': success, 'message': message})
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

@login_required
def invite_collaborator(request, trip_id):
    trip = get_object_or_404(inputTrip, id=trip_id, user=request.user)

    if request.method == 'POST':
        form = CollabInviteForm(request.POST, user=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                context = {
                    'destination': trip.destination,
                    'start_date': trip.start_date,
                    'end_date': trip.end_date,
                    'inviter': request.user.get_full_name() or request.user.username,
                    'signup_url': request.build_absolute_uri('/accounts/signup'),
                    'site_name': 'TravelMate',
                    'email': email,
                    'user': request.user,
                }

                subject = render_to_string(
                    'trips/collabinvite/collab_invite_subject.txt',
                    context
                ).strip()

                subject = ''.join(subject.splitlines())

                message = render_to_string(
                    'trips/collabinvite/collab_invite_email.txt',
                    context
                )

                from django.core.mail import EmailMultiAlternatives
                email_message = EmailMultiAlternatives(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    headers={'Reply-To': settings.DEFAULT_FROM_EMAIL},
                )
                email_message.send(fail_silently=False)

                messages.success(request, f'Invitation sent to {email}!')
                return redirect('edit_trip', trip_id=trip.id)

            except Exception as e:
                messages.error(request, 'Failed to send invitation')
                if settings.DEBUG:
                    print(f"Email error: {str(e)}")
                return redirect('edit_trip', trip_id=trip.id)

    return redirect('edit_trip', trip_id=trip.id)