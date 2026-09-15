from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active_agent')
    list_filter = ('role', 'is_active_agent')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
