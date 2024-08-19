from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path

from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.chat, name='chat'),
    path('profile', views.my_profile_view, name='my_profile'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('update', views.update_profile, name='update-profile'),
    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done', PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'), name='password_change_done'),
]
