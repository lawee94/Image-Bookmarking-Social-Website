from django.contrib import admin
from . import views
from django.urls import path
from django.shortcuts import render
from .models import CustomUser, Contact
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass

# Overriding and extending User Model
class CustomUserAdmin(UserAdmin):
    UserAdmin.fieldsets += ('Custom Fieldsets', { 'fields': ('date_of_birth', 'photo')}),
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [ 'username', 'email', 'first_name']
    

    #Mark user as active
    def make_active(modeladmin, request, queryset): 
        queryset.update(is_active = 1) 
        messages.success(request, "Selected User(s) Marked as Active Successfully !!") 
    
    #Mark user as inactive
    def make_inactive(modeladmin, request, queryset): 
        queryset.update(is_active = 0) 
        messages.success(request, "Selected User(s) Marked as Inactive Successfully !!") 
    
    #Set user as a staff
    def make_staff(modeladmin, request, queryset): 
        queryset.update(is_staff = 1) 
        messages.success(request, "Selected User(s) Marked as Staff Successfully !!") 
  
    #Unset user as staff
    def make_notstaff(modeladmin, request, queryset): 
        queryset.update(is_staff = 0) 
        messages.success(request, "Selected User(s) Unmarked as Staff Successfully !!") 
  
    #Registering actions
    admin.site.add_action(make_active, "Make Active") 
    admin.site.add_action(make_inactive, "Make Inactive") 
    admin.site.add_action(make_staff, "Make Staff") 
    admin.site.add_action(make_notstaff, "Unmark as Staff") 


admin.site.register(CustomUser, CustomUserAdmin)