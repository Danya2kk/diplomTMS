from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import (Profile, Friendship, Mediafile, News, Comment, Reaction,
                     Group, Mail, GroupMembership)

"""Добавить сигналы, чтобы профиль автоматически создавался при регистрации
 (но в модели Profile нужно разрешить чтобы поля были пустыми)"""
#
#
# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()

"""Функции для инвалидации кэша"""

def set_cache_with_key(cache_key, data, timeout=86400):
    """Утилитарная функция для кэширования данных с сохранением ключа."""
    cache.set(cache_key, data, timeout)
    cache_keys = cache.get('cache_keys', [])
    if cache_key not in cache_keys:
        cache_keys.append(cache_key)
        cache.set('cache_keys', cache_keys, timeout)

@receiver(post_save, sender=Profile)
@receiver(post_save, sender=Friendship)
@receiver(pre_delete, sender=Profile)
@receiver(pre_delete, sender=Friendship)
def clear_profile_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша при изменении/удалении профиля и дружбы."""
    if isinstance(instance, Profile):
        # Удаляем кэшированный профиль и список друзей
        cache.delete(f"profile_{instance.user.username}")
        cache.delete(f"friends_{instance.user.username}")

    if isinstance(instance, Friendship):
        # Удаляем кэш для обоих дружбанов
        cache.delete(f"friends_{instance.profile_one.user.username}")
        cache.delete(f"friends_{instance.profile_two.user.username}")


@receiver(post_save, sender=Mediafile)
@receiver(post_delete, sender=Mediafile)
def clear_media_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша фотографий при их удалении или добавлении"""
    username = instance.profile.user.username
    cache_key = f"media_{username}"
    cache.delete(cache_key)

@receiver(post_save, sender=News)
@receiver(pre_delete, sender=News)
def clear_news_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша списка новостей при их удалении или добавлении"""
    # Удаляем все ключи кэша
    cache_keys = cache.get('cache_keys', [])
    for key in cache_keys:
        cache.delete(key)
    # Очистим список ключей
    cache.delete('cache_keys')


@receiver(post_save, sender=News)
@receiver(pre_delete, sender=News)
def clear_news_detail_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей новости при их удалении или измении"""
    news_id = instance.news.id
    cache_key = f"news_detail_{news_id}"
    # Очистим список ключей
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Comment)
@receiver([post_save, post_delete], sender=Reaction)
def clear_news_detail_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей новости при  удалении или измении реакции или комментария"""
    cache_key = f"news_detail_{instance.news.id}"  # Очищаем кэш для конкретной новости
    cache.delete(cache_key)


@receiver(post_save, sender=Group)
@receiver(pre_delete, sender=Group)
def clear_group_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша списка групп при их удалении или измении"""
    # Удаляем все ключи кэша
    cache_keys = cache.get('cache_keys', [])
    for key in cache_keys:
        cache.delete(key)
    # Очистим список ключей
    cache.delete('cache_keys')

@receiver(post_save, sender=Profile)
@receiver(post_delete, sender=Profile)
def clear_profile_list_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей списка профилей их удалении или измении"""
    cache_key = f"profile_list_"
    # Удаляем конкретный ключ
    cache.delete(cache_key)

@receiver(pre_save, sender=GroupMembership)
@receiver(pre_delete, sender=GroupMembership)
def clear_group_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей группы при удалении или измении участников группы"""
    group_id = instance.group.id
    cache_key = f"group_detail_{group_id}"
    # Удаляем конкретный ключ из кэша
    cache.delete(cache_key)

@receiver(pre_save, sender=Group)
@receiver(pre_delete, sender=Group)
def clear_group_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей группы при удалении или измении конкретной группы"""
    cache_key = f"group_detail_{instance.id}"
    # Удаляем конкретный ключ из кэша
    cache.delete(cache_key)


@receiver(pre_save, sender=Mail)
def clear_mail_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша списка писем"""
    # Если письмо уже существует, обновляем его
    if instance.pk:
        try:
            old_instance = Mail.objects.get(pk=instance.pk)
            # Удаляем кэш для предыдущих значений, если изменены отправитель или получатель
            cache.delete(f"recipient_mail_{old_instance.recipient.id}")
            cache.delete(f"sender_mail_{old_instance.sender.id}")
        except Mail.DoesNotExist:
            pass

    # Удаляем кэш для нового или изменённого письма
    if instance.recipient:
        cache.delete(f"recipient_mail_{instance.recipient.id}")
    if instance.sender:
        cache.delete(f"sender_mail_{instance.sender.id}")


@receiver(pre_delete, sender=Mail)
def clear_mail_detail_cache(sender, instance, **kwargs):
    """ Функция инвалидации кэша деталей письма при удалении"""
    cache_key = f"mail_detail_{instance.id}"
    # Удаляем конкретный ключ из кэша
    cache.delete(cache_key)