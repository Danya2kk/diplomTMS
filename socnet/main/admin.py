from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Mediafile, Comment, FriendshipStatus
from .models import User, Profile, News, Tag, PrivacyLevel, Interest


# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', )


@admin.register(PrivacyLevel)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', )


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', )


admin.site.register(User, UserAdmin)
admin.site.register(Mediafile)

admin.site.register(News)
admin.site.register(Tag)

admin.site.register(Comment)



admin.site.register(FriendshipStatus)