from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetOTP, Vendor, Reward, CheckIn, RewardRedemption, Notification

# ---------------- Custom User Admin ----------------
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Preferences', {'fields': ('receive_notifications',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# ---------------- Register Models ----------------
admin.site.register(User, UserAdmin)
admin.site.register(PasswordResetOTP)
admin.site.register(Vendor)
admin.site.register(Reward)
admin.site.register(CheckIn)
admin.site.register(RewardRedemption)
admin.site.register(Notification)
