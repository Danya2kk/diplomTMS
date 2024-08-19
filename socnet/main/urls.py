from django.urls import path

from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.chat, name='chat'),
    path('profile', views.my_profile_view, name='my_profile'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('update', views.update_profile, name='update-profile'),
]
