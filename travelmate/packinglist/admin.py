from django.contrib import admin
from .models import Item, inputTrip  # Make sure to import inputTrip


class TripFilter(admin.SimpleListFilter):
    title = 'Trip'  # Human-readable title
    parameter_name = 'trip'  # URL parameter name

    def lookups(self, request, model_admin):
        # Get all unique trips that have items
        trips = inputTrip.objects.filter(items__isnull=False).distinct()
        return [(trip.id, f"{trip.destination}:[{trip.user}] - ({trip.start_date} to {trip.end_date})") for trip in trips]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(trip_id=self.value())
        return queryset


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "trip_info",  # Custom method
        "is_ai_suggested",
    )
    list_filter = (
        "is_ai_suggested",
        "user",
        TripFilter,  # Add our custom trip filter
    )
    search_fields = ("name", "description", "trip__destination")
    ordering = ("trip", "-is_ai_suggested", "name")  # Primary sort by trip

    # Add trip to autocomplete_fields if you have many trips
    autocomplete_fields = ['trip']

    # Custom method to display trip info
    def trip_info(self, obj):
        if obj.trip:
            return f"{obj.trip.destination} - ({obj.trip.start_date} to {obj.trip.end_date})"
        return "No trip"

    trip_info.short_description = 'Trip'
    trip_info.admin_order_field = 'trip'  # Allows column sorting

    # Custom change list template
    change_list_template = "admin/items/change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            "ai_count": Item.objects.filter(is_ai_suggested=True).count(),
            "user_count": Item.objects.filter(is_ai_suggested=False).count(),
            "trip_count": inputTrip.objects.count(),
        })
        return super().changelist_view(request, extra_context)

    # Add trip to raw_id_fields if you have many trips
    # raw_id_fields = ['trip']


admin.site.register(Item, ItemAdmin)


# Also register the Trip model if you want to manage trips in admin
class TripAdmin(admin.ModelAdmin):
    list_display = ('destination', 'start_date', 'end_date', 'user')
    list_filter = ('user',)
    search_fields = ('destination',)
    date_hierarchy = 'start_date'