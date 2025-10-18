from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User 
# Import User model từ users/models.py
admin.site.register(User, UserAdmin)