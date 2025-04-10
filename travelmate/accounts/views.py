from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required

def signup(request):
    template_data={}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = RegisterForm
        return render(request, 'accounts/signup.html', {'template_data':template_data})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request,'accounts/signup.html', {'template_data':template_data})     
def login(request):
    template_data={}
    template_data['title'] = 'Log In'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data':template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data':template_data})
        auth_login(request,user)
        return redirect('')
