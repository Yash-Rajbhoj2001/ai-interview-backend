from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User

    ordering = ('email',)

    list_display = ('email', 'plan', 'billing_cycle', 'is_staff')
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Plan Info', {'fields': ('plan', 'interviews_remaining', 'billing_cycle')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'plan', 'billing_cycle'),
        }),
    )


admin.site.register(User, UserAdmin)