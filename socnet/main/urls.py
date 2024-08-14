from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import  RegisterAPIView, LoginAPIView

from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.index, name='chat'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
]