from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path, include
from main import views
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet)
router.register(r'activities', views.ActivityLogViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'friendships', views.FriendshipViewSet)
router.register(r'notifications', views.NotificationViewSet)


urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.LoginUser.as_view(), name='login'),     # для
    path('logout', LogoutView.as_view(), name='logout'),
    path('chat', views.chat, name='chat'),
    path('profile', views.my_profile_view, name='my_profile'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('update', views.update_profile, name='update-profile'),
    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done', PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'), name='password_change_done'),
    path('news/<int:pk>', views.news_detail, name='news_detail'),
    path('news', views.news_list, name='news'),
    path('api/news/', views.news_list_api, name='news_list_api'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('<int:news_pk>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:comment_pk>/edit/', views.comment_edit, name='comment_edit'),
    # path('<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:content_type_id>/<int:object_id>/<str:reaction_type>/create/', views.reaction_create,
         name='reaction_create'),
    path('<int:content_type_id>/<int:object_id>/count/', views.reaction_count, name='reaction_count'),
    path('api/', include(router.urls)),
]
