from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import (Comment, Friendship, FriendshipStatus, Group,
                     GroupMembership, Interest, Mail, Mediafile, News,
                     PrivacyLevel, Profile, Status, Tag, User, ActivityLog_norest, Notification_norest)


# добавляем таблицы для вывода в админке

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

# таблицы для логирования действий пользователей выводи подробнее с возможностью сортировки

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'notification_type', 'content', 'timestamp', 'read')
    search_fields = ('profile__user__username', 'content')  # Поиск по имени пользователя и содержимому
    list_filter = ('notification_type', 'read', 'timestamp')  # Фильтрация по типу уведомления, статусу прочтения и времени
    ordering = ('-timestamp',)  # Сортировка по времени от новых к старым

admin.site.register(Notification_norest, NotificationAdmin)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('profile', 'action_type', 'description', 'timestamp')
    search_fields = ('profile__user__username', 'description')  # Поиск по имени пользователя и описанию действия
    list_filter = ('action_type', 'timestamp')  # Фильтрация по типу действия и времени
    ordering = ('-timestamp',)  # Сортировка по времени от новых к старым

admin.site.register(ActivityLog_norest, ActivityLogAdmin)


