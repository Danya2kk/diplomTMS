from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from django.contrib import admin


urlpatterns = [
    path("creator/", admin.site.urls),
    path("", include("main.urls")),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
