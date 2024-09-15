from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter

from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings

from api import views

# Регистрируем ViewSet'ы
routerapi = DefaultRouter()
routerapi.register(r"profiles", views.ProfileViewSet)
routerapi.register(r"activities", views.ActivityLogViewSet)
routerapi.register(r"groups", views.GroupViewSet)
routerapi.register(r"friendships", views.FriendshipViewSet, basename="friendship")
routerapi.register(r"notifications", views.NotificationViewSet)

# Подключаем router и swagger
urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Добавляем пути из router
    path('', include(routerapi.urls)),  # <-- подключаем маршруты API
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
