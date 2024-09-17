from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Profile, Friendship, Mediafile, News, Comment, Reaction

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

@receiver(post_save, sender=Profile)
@receiver(post_save, sender=Friendship)
def clear_profile_cache(sender, instance, **kwargs):
    cache.delete(f"profile_{instance.user.username}") # Удаляем кэшированный профиль
    cache.delete(f"friends_{instance.user.username}") # Удаляем кэшированный список друзей

@receiver(post_save, sender=Mediafile)
@receiver(post_delete, sender=Mediafile)
def clear_media_cache(sender, instance, **kwargs):
    username = instance.profile.user.username
    cache_key = f"media_{username}"
    cache.delete(cache_key)
    print(f"Cache deleted for key: {cache_key}")

@receiver(post_save, sender=News)
@receiver(post_delete, sender=News)
def clear_media_cache(sender, instance, **kwargs):
    print('Cache invalidation triggered')
    username = instance.profile.user.username
    cache_key = f"media_{username}"

    # Удаляем конкретный ключ
    cache.delete(cache_key)

    # Также удаляем все ключи из списка
    cache_keys = cache.get('cache_keys', [])
    if cache_key in cache_keys:
        cache_keys.remove(cache_key)
        cache.set('cache_keys', cache_keys, 60 * 60)  # Обновляем список ключей на 1 час

    print(f"Cache deleted for key: {cache_key}")

@receiver([post_save, post_delete], sender=Comment)
@receiver([post_save, post_delete], sender=Reaction)
def clear_news_detail_cache(sender, instance, **kwargs):
    cache_key = f"news_detail_{instance.news.id}"  # Очищаем кэш для конкретной новости
    cache.delete(cache_key)