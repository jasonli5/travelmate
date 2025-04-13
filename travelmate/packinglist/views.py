from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item
from django.http import JsonResponse
from .api_utils import get_ai_suggestions
from django.views.decorators.http import require_POST

@login_required
def create_item(request):
    if request.method == 'POST':
        if 'existing_item_id' in request.POST:
            # Handle adding existing AI item
            item = get_object_or_404(Item, pk=request.POST['existing_item_id'], user=request.user)
            item.is_ai_suggested = False
            item.save()
            return JsonResponse({'status': 'success'})

    if request.method == 'POST' and request.POST.get('name') and request.POST.get('description'):
        item = Item(
            name=request.POST['name'],
            description=request.POST['description'],
            user=request.user,
            is_ai_suggested = request.POST['is_ai_suggested'],
        )
        item.save()
        print("Adding Items!")
        return redirect('packing_list')
    else:
        print("REDIRECTING BECAUSE:")
        if request.method != 'POST': print("- Not a POST request")
        if not request.POST.get('name'): print("- 'name' is missing/empty")
        if not request.POST.get('description'): print("- 'description' is missing/empty")
        return redirect('packing_list')


def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)  # Only allow owner to edit

    if request.method == 'POST':
        item.name = request.POST.get('name', item.name)
        item.description = request.POST.get('description', item.description)
        item.save()
        return redirect('packing_list')

    # For GET requests, show edit form (handled in template modal)
    return redirect('packing_list')


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)  # Only allow owner to delete
    if request.method == 'POST':
        item.delete()

    return redirect('packing_list')
@login_required
def ai_suggest_items(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        days = int(request.POST.get('days', 3))
        count = int(request.POST.get('count', 6))
        # Store location in session
        request.session['last_location'] = location
        existing_items = list(Item.objects.filter(
            user=request.user
        ).values('name', 'description'))

        # Get AI suggestions
        suggestions = get_ai_suggestions("Japan", "December", 6, existing_items)
        print(existing_items)
        # Return JSON for AJAX handling
        return JsonResponse(suggestions)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def create_ai_item(request):
    if request.method == 'POST':
        item = Item(
            name=request.POST.get('title'),
            description=request.POST.get('description'),
            user=request.user,
            is_ai_suggested=True  # Add this field to your model
        )
        item.save()
        return redirect(packing_list)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def packing_list(request):
    # Get only items belonging to the current user
    user_items = Item.objects.filter(user=request.user, is_ai_suggested=False).order_by('id')
    ai_items = Item.objects.filter(user=request.user, is_ai_suggested=True).order_by('id')

    context = {
        'items': user_items,
        'ai_items': ai_items,
        'default_location': request.session.get('last_location', '')
    }

    return render(request, 'packinglist/packing_list.html', context)