from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            ('Personal info'),
            {'fields': ('first_name', 'last_name', 'email')},
        ),
        (
            ('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                ),
            },
        ),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'email',
                ),
            },
        ),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ['username']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)
