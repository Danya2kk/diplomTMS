from django.urls import path
from main import views


urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.index, name='chat'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]