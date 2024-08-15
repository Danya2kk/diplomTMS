from django.urls import path

from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.chat, name='chat'),
    path('profile/<str:username>', views.profile_view, name='profile')
]
