from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .forms import RegisterForm, CustomUserChangeForm

#RegisterForm is serving as UserCreationForm to maintain email check logic

UserAdmin.add_form = RegisterForm

#Editing fieldsets of UserAdmin form to include email when "Add User" clicked
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('email', 'username', 'password1', 'password2',)
    }),
)

UserAdmin.form = CustomUserChangeForm
UserAdmin.fieldsets  = (
    (None, {
        'classes': ('wide',),
        'fields': ('email', 'username', 'password')
    }),
)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)