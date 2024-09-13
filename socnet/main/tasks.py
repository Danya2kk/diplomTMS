from datetime import timedelta
from django.utils import timezone
from celery import shared_task

from .models import ArchiveChat, ArchivedMail, Chat, Mail, StatusProfile

@shared_task
def archive_chat():
    chats = Chat.objects.all()
    for chat in chats:
        ArchiveChat.objects.create(
            created_at=chat.created_at, profile=chat.profile, group=chat.group
        )
    chats.delete()


@shared_task
def archive_mail():
    mails = Mail.objects.all()
    for mail in mails:
        ArchivedMail.objects.create(
            sender=mail.sender,
            recipient=mail.recipient,
            content=mail.content,
            timestamp=mail.timestamp,
            parent=mail.parent,
            is_read=mail.is_read,
            is_deleted_sender=mail.is_deleted_sender,
        )
    mails.delete()


@shared_task
def clean_mail():
    six_months_ago = timezone.now() - timedelta(days=180)
    mails_to_delete = Mail.objects.filter(timestamp__lt=six_months_ago)
    for mail in mails_to_delete:
        ArchivedMail.objects.create(
            sender=mail.sender,
            recipient=mail.recipient,
            content=mail.content,
            timestamp=mail.timestamp,
            parent=mail.parent,
            is_read=mail.is_read,
            is_deleted_sender=mail.is_deleted_sender,
        )
    mails_to_delete.delete()


@shared_task
def update_online_status():
    # Определяем пороговое время для определения, что пользователь неактивен
    time_threshold = timezone.now() - timedelta(minutes=5)

    # Фильтруем профили, где last_updated старше порогового времени
    profiles_to_update = StatusProfile.objects.filter(
        last_updated__lt=time_threshold, is_online=True
    )

    # Обновляем статус is_online на False для этих профилей
    profiles_to_update.update(is_online=False)
