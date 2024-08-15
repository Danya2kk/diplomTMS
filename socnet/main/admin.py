from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, PrivacyLevel, Interest

# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname')


admin.site.register(User, UserAdmin)
# admin.site.register(Profile, ProfileAdmin)
admin.site.register(PrivacyLevel)
admin.site.register(Interest)
