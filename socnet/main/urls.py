
from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views
from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path, include

from main import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet)
router.register(r'activities', views.ActivityLogViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'friendships', views.FriendshipViewSet, basename='friendship')
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('', views.index, name='home'),
    path('chat', views.index, name='chat'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('chat', views.chat, name='chat'),
    path('profile_list', views.profile_list, name='profile_list'),
    path('profile', views.my_profile_view, name='my_profile'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('profile/photo/<str:username>', views.profile_media, name='profile-photo'),
    path('profile/photo/add_media/', views.profile_add_media, name='profile_add_media'),

    path('update', views.update_profile, name='update-profile'),
    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done', PasswordChangeDoneView.as_view(template_name='main/password_change_done.html'), name='password_change_done'),
    path('news/<int:pk>', views.news_detail, name='news_detail'),
    path('news', views.news_list, name='news'),
    path('api/news/', views.news_list_api, name='news_list_api'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('news/<int:news_id>/add_comment/', views.add_comment, name='add_comment'),
    path('groups_list/', views.GroupListView.as_view(), name='groups_list'),
    path('group/<int:pk>', views.GroupDetailView, name='group'),
    path('groups/invite/<str:username>/<int:pk>/', views.GroupInvite, name='group_invite'),
    path('groups/join/<int:pk>/', views.join_group, name='group_join'),
    path('groups/group_leave/<int:pk>/', views.leave_group, name='group_leave'),
    path('groups/group_kik/<str:username>/<int:pk>/', views.kik_group, name='group_kik'),
    path('groups/group_create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/group_update/<int:pk>/', views.GroupUpdateView.as_view(), name='group_update'),
    path('groups/group_delete/<int:pk>/', views.GroupDeleteView.as_view(), name='group_delete'),



    # path('<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    # path('reaction/<int:object_id>/<str:model_name>/<str:reaction_type>/', views.add_reaction, name='add_reaction'),
    path('reaction/toggle/', views.reaction_toggle, name='reaction_toggle'),
    # path('<int:content_type_id>/<int:object_id>/count/', views.reaction_count, name='reaction_count'),
    path('send-message/', views.SendMailView.as_view(), name='send_message'),
    path('mailbox/', views.UserMailView, name='mailbox'),
    path('mailbox/sender_mail', views.sender_mail, name='sender_mail'),
    path('mailbox/recipient_mail', views.recipient_mail, name='recipient_mail'),

    path('mailbox/send_mail', views.send_mail, name='send_mail'),
    path('mailbox/send_mail_parent', views.send_mail_parent, name='send_mail_parent'),
    path('mailbox/message/<int:mail_id>/', views.message_detail, name='message_detail'),

    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('update_status/', views.update_status, name='update_status'),




    path('', include(router.urls)),


    # re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]