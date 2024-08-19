from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, News, Tag, PrivacyLevel, Interest

# Register your models here.


admin.site.register(User, UserAdmin)
admin.site.register(Profile)


admin.site.register(News)
admin.site.register(Tag)

admin.site.register(PrivacyLevel)
admin.site.register(Interest)


