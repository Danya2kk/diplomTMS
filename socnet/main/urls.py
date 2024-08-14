from django.urls import path
from .views import RegisterView, LoginView, RegisterAPIView, LoginAPIView

from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.index, name='chat'),
    path('api/register/', RegisterAPIView.as_view(), name='register_api'),
    path('api/login/', LoginAPIView.as_view(), name='login_api'),
    path('register/', RegisterView.as_view(), name='register_view'),
    path('login/', LoginView.as_view(), name='login_view'),
]


