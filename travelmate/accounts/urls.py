from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from accounts.views import CustomLoginView, ResetPasswordView
from accounts.forms import LoginForm

urlpatterns = [
    path('signup/', views.signup, name='accounts.signup'),
    path('login/', CustomLoginView.as_view(redirect_authenticated_user=True, template_name='accounts/login.html', authentication_form=LoginForm), name='accounts.login'),
    path('profile/',views.profile, name='accounts.profile'),
    path('logout/', views.logout, name='accounts.logout'),
    path('password-reset/', ResetPasswordView.as_view(), name='accounts.reset'),
]