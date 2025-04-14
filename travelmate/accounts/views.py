from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


class RegisterView(View):
    form_class = RegisterForm
    initial = {"key": "value"}
    template_name = "accounts/signup.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get("username")
            user.email = form.cleaned_data.get("email")
            user.save()
            return redirect("accounts.login")

        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        self.request.session.set_expiry(0)
        self.request.session.modified = True
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/reset_email.html"
    subject_template_name = "accounts/email_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("accounts.login")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


def logout(request):
    auth_logout(request)
    return redirect("home.index")
