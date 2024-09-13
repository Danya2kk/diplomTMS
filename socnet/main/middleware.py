from django.utils import timezone
from .models import StatusProfile


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:

            status_profile = StatusProfile.objects.get(profile=request.user.profile)
            status_profile.is_online = True
            status_profile.last_updated = timezone.now()
            status_profile.save()

        response = self.get_response(request)
        return response
