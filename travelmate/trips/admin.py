from django.contrib import admin
from .models import inputTrip, travelRecommendations
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from django.contrib import messages
from django.templatetags.static import static
import json
import os
from django.conf import settings
from trips.tasks import task_creation
from django.http import HttpResponseRedirect

DEFAULT_TRIPS = {
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

# Path to JSON file
TRIPS_FILE = os.path.join(settings.BASE_DIR, 'trips/jsons/predefined_trips.json')

@admin.action(description='Send trip reminders')
def send_reminders(modeladmin, request, queryset):
    task_creation()
    modeladmin.message_user(request, "Reminder tasks created successfully", messages.SUCCESS)
    return HttpResponseRedirect(request.get_full_path())
def load_predefined_trips():
    """Load trips from JSON file or return default if file doesn't exist"""
    try:
        # Check if file exists and has content
        if os.path.exists(TRIPS_FILE) and os.path.getsize(TRIPS_FILE) > 0:
            with open(TRIPS_FILE, 'r') as f:
                return json.load(f)

        # If file doesn't exist or is empty, create it with defaults
        save_predefined_trips(DEFAULT_TRIPS)
        return DEFAULT_TRIPS

    except (json.JSONDecodeError, IOError) as e:
        # If there's any error reading, recreate the file
        save_predefined_trips(DEFAULT_TRIPS)
        return DEFAULT_TRIPS


def save_predefined_trips(trips_data):
    """Save trips to JSON file atomically to prevent corruption"""
    try:
        # Create a temporary file
        temp_file = f"{TRIPS_FILE}.tmp"

        # Write to temporary file
        with open(temp_file, 'w') as f:
            json.dump(trips_data, f, indent=2)

        # Atomic rename (works on Unix and Windows)
        if os.path.exists(TRIPS_FILE):
            os.replace(temp_file, TRIPS_FILE)
        else:
            os.rename(temp_file, TRIPS_FILE)

    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise e

@admin.register(inputTrip)
class TripAdmin(admin.ModelAdmin):
    actions = [send_reminders]
    # List display configuration
    list_display = ('destination_with_link', 'user', 'weather_preview', 'date_range', 'created_at')
    list_filter = (('start_date', DateFieldListFilter), ('end_date', DateFieldListFilter), 'user')
    search_fields = ('destination', 'user__username')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ('weather_prettified',)  # Add this line

    # Form display configuration
    fieldsets = (
        ('Trip Information', {
            'fields': ('user', 'destination', 'considerations', ('start_date', 'end_date'))
        }),
        ('Weather Data', {
            'fields': ('weather_prettified',),
            'classes': ('collapse',),  # Makes this section collapsible
        }),
    )

    # Custom methods for list display
    def destination_with_link(self, obj):
        return format_html('<a href="{}">{}</a>', f'/admin/trips/inputtrip/{obj.id}/change/', obj.destination)

    destination_with_link.short_description = 'Destination'
    destination_with_link.admin_order_field = 'destination'

    def date_range(self, obj):
        return f"{obj.start_date.strftime('%b %d, %Y')} to {obj.end_date.strftime('%b %d, %Y')}"

    date_range.short_description = 'Trip Dates'

    def weather_preview(self, obj):
        if obj.weather:
            try:
                weather_data = json.loads(obj.weather)
                return format_html(
                    '<span title="{}">🌤️ Weather Data ({})</span>',
                    weather_data.get('location', 'N/A'),
                    len(weather_data.get('reports', [])))
            except json.JSONDecodeError:
                return "Invalid weather data"
        return "No weather data"
    weather_preview.short_description = 'Weather'

    def weather_prettified(self, obj):
        if obj.weather:
            try:
                weather_data = json.loads(obj.weather)
                pretty_weather = json.dumps(weather_data, indent=2)
                return format_html('<pre>{}</pre>', pretty_weather)
            except json.JSONDecodeError:
                return "Invalid weather data format"
        return "No weather data available"
    weather_prettified.short_description = 'Weather Data'

    # Customize the add/edit form
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'weather_prettified')
        return ()

    def weather_prettified(self, obj):
        if not obj.weather:
            return "No weather data available"

        try:
            weather_data = json.loads(obj.weather)
            location = weather_data.get('location', 'Unknown location')
            reports = weather_data.get('reports', [])

            if not reports:
                return format_html('<div class="alert alert-info">No weather reports available</div>')

            html = f"""
            <div class="weather-admin-container">
                <h4>{location}</h4>
                <div class="weather-reports">
            """

            for report in reports:
                date = report.get('date', 'Unknown date')
                report_text = report.get('report', 'No data')

                # Format the report text with HTML
                formatted_report = []
                for line in report_text.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        formatted_report.append(f"""
                            <div class="weather-line">
                                <span class="weather-key">{key}:</span>
                                <span class="weather-value">{value.strip()}</span>
                            </div>
                        """)

                html += f"""
                <div class="weather-report-card">
                    <h5>{date}</h5>
                    <div class="weather-details">
                        {''.join(formatted_report)}
                    </div>
                </div>
                """

            html += """
                </div>
            </div>
            """

            return format_html(html)

        except json.JSONDecodeError:
            return format_html('<div class="alert alert-danger">Invalid weather data format</div>')

    weather_prettified.short_description = 'Weather Forecast'
    weather_prettified.allow_tags = True


    # Add this to your Media class
    class Media:
        css = {
            'all': [
                'css/admin-trips.css',
            ]
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js',
        )


@admin.register(travelRecommendations)
class TravelRecommendationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'image_preview', 'predefined_trip_actions')
    search_fields = ('name', 'description')
    list_per_page = 25
    actions = ['create_predefined_trips', 'update_predefined_trips']

    readonly_fields = ('predefined_trip_info',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image')
        }),
        ('Predefined Trip Information', {
            'fields': ('predefined_trip_info',),
            'classes': ('collapse',),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        trips_data = load_predefined_trips()
        if obj and obj.name.lower() in trips_data:
            return self.fieldsets
        return (self.fieldsets[0],)

    def description_preview(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description

    description_preview.short_description = 'Description'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius: 8px;"/>', obj.image.url)
        return "No image"

    image_preview.short_description = 'Image'

    def predefined_trip_actions(self, obj):
        trips_data = load_predefined_trips()
        key = obj.name.lower()
        if key in trips_data:
            return format_html(
                '<a class="button" href="{}">Edit Predefined</a>',
                f'{obj.id}/edit_predefined/'
            )
        return ""

    predefined_trip_actions.short_description = 'Predefined Trip Actions'
    predefined_trip_actions.allow_tags = True

    def predefined_trip_info(self, obj):
        trips_data = load_predefined_trips()
        key = obj.name.lower()
        if key in trips_data:
            trip = trips_data[key]
            return format_html(
                """
                <table>
                    <tr><th>Field</th><th>Value</th></tr>
                    <tr><td>Destination</td><td>{}</td></tr>
                    <tr><td>Activities</td><td>{}</td></tr>
                    <tr><td>Duration</td><td>{} days</td></tr>
                </table>
                """,
                trip.get('destination', 'N/A'),
                trip.get('activities', 'N/A'),
                trip.get('duration', 'N/A')
            )
        return "Not a predefined trip"

    predefined_trip_info.short_description = 'Predefined Trip Details'
    predefined_trip_info.allow_tags = True

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/edit_predefined/',
                 self.admin_site.admin_view(self.edit_predefined),
                 name='edit_predefined_trip'),
        ]
        return custom_urls + urls

    def edit_predefined(self, request, object_id, *args, **kwargs):
        from django.shortcuts import redirect
        from django.template.response import TemplateResponse

        trips_data = load_predefined_trips()
        obj = travelRecommendations.objects.get(pk=object_id)
        key = obj.name.lower()

        if request.method == 'POST':
            try:
                if key in trips_data:
                    trips_data[key] = {
                        'destination': request.POST.get('destination', ''),
                        'activities': request.POST.get('activities', ''),
                        'duration': int(request.POST.get('duration', 7))
                    }
                    save_predefined_trips(trips_data)
                    messages.success(request, 'Predefined trip updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating predefined trip: {str(e)}')
            return redirect(f'/admin/trips/travelrecommendations/{object_id}/change/')

        # GET request
        predefined_data = trips_data.get(key, {})
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'original': obj,
            'predefined_data': predefined_data,
            'predefined_key': key,
        }
        return TemplateResponse(
            request,
            'trips/edit_predefined_trip.html',
            context
        )

    def create_predefined_trips(self, request, queryset):
        trips_data = load_predefined_trips()
        created = 0
        for obj in queryset:
            key = obj.name.lower()
            if key not in trips_data:
                trips_data[key] = {
                    'destination': obj.name,
                    'activities': f"Suggested activities for {obj.name}",
                    'duration': 7
                }
                created += 1

        if created > 0:
            save_predefined_trips(trips_data)

        self.message_user(
            request,
            f'Successfully created {created} predefined trip(s)',
            messages.SUCCESS
        )

    create_predefined_trips.short_description = 'Create predefined trips from selected'

    def update_predefined_trips(self, request, queryset):
        trips_data = load_predefined_trips()
        updated = 0
        for obj in queryset:
            key = obj.name.lower()
            if key in trips_data:
                trips_data[key]['destination'] = obj.name
                updated += 1

        if updated > 0:
            save_predefined_trips(trips_data)

        self.message_user(
            request,
            f'Successfully updated {updated} predefined trip(s)',
            messages.SUCCESS
        )

    update_predefined_trips.short_description = 'Update selected predefined trips'

    class Media:
        css = {
            'all': ['css/admin-trips.css']
        }