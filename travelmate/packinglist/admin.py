from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_ai_suggested')  # Only uses your model fields
    list_filter = ('is_ai_suggested', 'user')  # Filter sidebar
    search_fields = ('name', 'description')
    ordering = ('-is_ai_suggested', 'name')  # Groups AI items first

    # Custom change list template
    change_list_template = 'admin/items/change_list.html'

    # Add counts to admin view
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'ai_count': Item.objects.filter(is_ai_suggested=True).count(),
            'user_count': Item.objects.filter(is_ai_suggested=False).count()
        })
        return super().changelist_view(request, extra_context)


admin.site.register(Item, ItemAdmin)