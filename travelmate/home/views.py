from django.shortcuts import render,redirect
from trips.forms import InputForm

# Create your views here.
def index(request):
    template_data = {}
    template_data['title'] = 'TravelMate'
    form = InputForm()
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            form.save()
    template_data['form'] = form
    return render(request, 'home/index.html', {'template_data': template_data})
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})