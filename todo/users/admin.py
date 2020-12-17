from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Task

@admin.register(User)
class UserAdmin(UserAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin): 
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin): 
    pass