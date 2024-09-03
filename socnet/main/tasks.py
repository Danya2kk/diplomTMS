from celery import shared_task
from .models import Mail, Chat, ArchivedMail, ArchiveChat
from django.utils import timezone
from datetime import timedelta


@shared_task
def archive_chat():
    chats = Chat.objects.all()
    for chat in chats:
        ArchiveChat.objects.create(
            created_at=chat.created_at,
            profile=chat.profile,
            group=chat.group
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
            is_deleted_sender=mail.is_deleted_sender
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
            is_deleted_sender=mail.is_deleted_sender
        )
    mails_to_delete.delete()
