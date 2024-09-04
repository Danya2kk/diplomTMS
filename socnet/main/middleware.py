# main/middleware.py

from django.utils import timezone
from .models import StatusProfile

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                status_profile = StatusProfile.objects.get(profile=request.user.profile)
                status_profile.is_online = True
                status_profile.last_updated = timezone.now()
                status_profile.save()
            except StatusProfile.DoesNotExist:
                # Создаем новую запись в StatusProfile, если не существует
                StatusProfile.objects.create(
                    profile=request.user.profile,
                    is_online=True,
                    is_busy=False,
                    do_not_disturb=False,
                    last_updated=timezone.now()
                )

        response = self.get_response(request)
        return response
