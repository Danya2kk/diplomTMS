from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)


class PrivacyLevel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Interest(models.Model):
    name = models.CharField(max_length=255)


class Profile(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.TextField()
    age = models.IntegerField()
    gender = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    link = models.TextField()
    settings = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    privacy = models.ForeignKey(PrivacyLevel, on_delete=models.SET_NULL, null=True)
    interests = models.ManyToManyField(Interest)


class Mediafile(models.Model):
    profile = models.ForeignKey(Profile, related_name='media_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, choices=[('image', 'Image'), ('video', 'Video'), ('other', 'Other')])
    description = models.TextField()


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Отправлен запрос'),
        ('friends', 'Друзья'),
        ('blocked', 'Заблокирован'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent',)
    description = models.TextField(blank=True, null=True)
    profile_one = models.ForeignKey(Profile, related_name='friendship_one', on_delete=models.CASCADE)
    profile_two = models.ForeignKey(Profile, related_name='friendship_two', on_delete=models.CASCADE)


class Mail(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_read = models.BooleanField(default=False)
    is_deleted_sender = models.BooleanField(default=False)


class Group(models.Model):
    PUBLIC = 'public'
    PRIVATE = 'private'
    SECRET = 'secret'

    GROUP_TYPES = [
        (PUBLIC, 'Public'),
        (SECRET, 'Secret'),
        (PRIVATE, 'Private')
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='group_photos/', blank=True, null=True)
    group_type = models.CharField(max_length=10, choices=GROUP_TYPES, default=PUBLIC)
    creator = models.ForeignKey(Profile)
    rules = models.TextField(blank=True)


class Status(models.Model):
    ADMIN = 'admin'
    USER = 'user'

    STATUS_CHOICES = [
        (ADMIN, 'Administrator'),
        (USER, 'User'),
    ]
    name = models.CharField(max_length=20, choices=STATUS_CHOICES, default=USER)

    def __str__(self):
        return dict(self.STATUS_CHOICES).get(self.name, self.name)


class GroupMembership(models.Model):
    profile = models.ForeignKey(Profile, related_name='group_memberships', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='members', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, null=True, blank=True, on_delete=models.SET_NULL)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'group')


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    profile = models.ForeignKey(Profile, related_name='news_posts', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='news_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile, related_name='comments', on_delete=models.CASCADE)
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    HEART = 'heart'

    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (HEART, 'Heart'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('profile', 'content_type', 'object_id', 'reaction_type')


class StatusProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    do_not_disturb = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)


class Chat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, related_name='news_message', on_delete=models.CASCADE)


class Notification(models.Model):
    FRIEND_REQUEST = 'FR'
    MESSAGE = 'MSG'
    MENTION = 'MENT'

    NOTIFICATION_CHOICES = [
        (FRIEND_REQUEST, 'Friend Request'),
        (MESSAGE, 'Message'),
        (MENTION, 'Mention'),
    ]

    profile = models.ForeignKey(Profile, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class ActivityLog(models.Model):
    LOGIN = 'LOGIN'
    POST = 'POST'
    COMMENT = 'COMMENT'
    LIKE = 'LIKE'

    ACTION_CHOICES = [
        (LOGIN, 'Login'),
        (POST, 'Post Created'),
        (COMMENT, 'Comment Made'),
        (LIKE, 'Like'),
    ]

    profile = models.ForeignKey(Profile, related_name='activities', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
