from django.urls import path
from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path('', views.packing_list, name='packing_list'),
    path('item/create/', views.create_item, name='item_create'),
    path('item/<int:item_id>/edit/', views.edit_item, name='item_edit'),  # New
    path('item/<int:item_id>/delete/', views.delete_item, name='item_delete'),
    path('ai/suggest/', views.ai_suggest_items, name='ai_suggest'),
    path('ai/create/', views.create_ai_item, name='ai_create'),
]