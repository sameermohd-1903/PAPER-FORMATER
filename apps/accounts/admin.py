from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Teacher
@admin.register(Teacher)
class TeacherAdmin(UserAdmin):
    list_display = ['username', 'email', 'department', 'phone_number', 'date_joined']
    list_filter = ['department', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Teacher Info', {'fields': ('department', 'phone_number')}),
    )