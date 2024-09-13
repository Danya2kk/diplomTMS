from .models import (Comment, Friendship, FriendshipStatus, Group,
                     GroupMembership, Interest, Mail, Mediafile, News,
                     PrivacyLevel, Profile, Status, Tag, User)

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "firstname",
        "lastname",
    )


@admin.register(PrivacyLevel)
class PrivacyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(User, UserAdmin)

admin.site.register(Mediafile)

admin.site.register(News)
admin.site.register(Tag)

admin.site.register(Comment)
admin.site.register(Friendship)

admin.site.register(FriendshipStatus)
admin.site.register(Group)

# admin.site.register(Chat)
admin.site.register(Mail)

admin.site.register(GroupMembership)

admin.site.register(Status)
