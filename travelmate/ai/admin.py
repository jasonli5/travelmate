from django.contrib import admin

from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'trip', 'is_ai_suggested')
    search_fields = ('name', 'description')
    list_filter = ('is_ai_suggested',)
    list_per_page = 25