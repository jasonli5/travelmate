from django.contrib import admin
from .models import inputTrip, travelRecommendations
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from django.templatetags.static import static
import json

@admin.register(inputTrip)
class TripAdmin(admin.ModelAdmin):
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
class travelRecommendationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'image_preview')
    search_fields = ('name', 'description')

    def description_preview(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    description_preview.short_description = 'Description'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius: 8px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'