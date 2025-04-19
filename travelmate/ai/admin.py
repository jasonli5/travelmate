from django.contrib import admin

from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip')
    search_fields = ('name',)

