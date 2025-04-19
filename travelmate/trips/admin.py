# trips/admin.py
from django.contrib import admin
from .models import inputTrip, travelRecommendations
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from django.templatetags.static import static


@admin.register(inputTrip)
class TripAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = ('destination_with_link', 'user', 'considerations', 'date_range', 'created_at')
    list_filter = (('start_date', DateFieldListFilter), ('end_date', DateFieldListFilter), 'user')
    search_fields = ('destination', 'user__username')
    list_per_page = 25
    date_hierarchy = 'created_at'

    # Form display configuration
    fieldsets = (
        ('Trip Information', {
            'fields': ('user', 'destination', 'considerations', ('start_date', 'end_date'))
        }),
        # ('Activities', {
        #     'fields': ('activities',),
        #     'classes': ('wide', 'extrapretty'),
        # }),
    )

    # Custom methods for list display
    def destination_with_link(self, obj):
        return format_html('<a href="{}">{}</a>', f'/admin/trips/inputtrip/{obj.id}/change/', obj.destination)

    destination_with_link.short_description = 'Destination'
    destination_with_link.admin_order_field = 'destination'

    def date_range(self, obj):
        return f"{obj.start_date.strftime('%b %d, %Y')} to {obj.end_date.strftime('%b %d, %Y')}"

    date_range.short_description = 'Trip Dates'

    def activities_preview(self, obj):
        return obj.activities[:50] + ('...' if len(obj.activities) > 50 else '')

    activities_preview.short_description = 'Activities Preview'

    # Customize the add/edit form
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at',)
        return ()

    # Optional: Add custom CSS
    class Media:
        css = {
            'all': ('css/admin-trips.css',)
        }

@admin.register(travelRecommendations)
class travelRecommendationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'image_preview')
    search_fields = ('name', 'description')

    def description_preview(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    description_preview.short_description = 'Description'

    def image_preview(self, obj):
        if obj.image:
            image_url = static(f'img/{obj.image}')
            return format_html('<img src="{}" width="100" style="border-radius: 8px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'