from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

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
class CustomLoginView(LoginView):
    form_class = LoginForm
    def form_valid(self, form):
        self.request.session.set_expiry(0)
        self.request.session.modified = True
        return super(CustomLoginView, self).form_valid(form)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('accounts.login')


@login_required
def profile(request):
    return render(request,'accounts/profile.html')

def logout(request):
    auth_logout(request)
    return redirect('home.index')
