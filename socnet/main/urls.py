from django.views.decorators.cache import cache_page
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from main import views


router = DefaultRouter()
# этот роутер используется для работы с дружбой
router.register(r"friendships", views.FriendshipViewSet, basename="friendship")

urlpatterns = [
    path("",views.index, name="home"),
    path("chat", views.index, name="chat"),
    path("register/", views.RegisterUser.as_view(), name="register"),
    path("login/", views.LoginUser.as_view(), name="login"),
    path("logout/", views.LogoutUser.as_view(), name="logout"),
    path("group/chat/<int:pk>", views.chat, name="chat"),
    path("profile_list",views.profile_list, name="profile_list"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path("profile/photo/<str:username>", views.profile_media, name="profile-photo"),
    path("profile/photo/add_media/", views.profile_add_media, name="profile_add_media"),
    path("update", views.update_profile, name="update-profile"),
    path("password-change/", views.UserPasswordChange.as_view(), name="password_change"),
    path("news/<int:pk>", views.news_detail, name="news_detail"),
    path("news", views.NewsListView.as_view(), name="news"),
    path("api/news/", views.news_list_api, name="news_list_api"),
    path("news/<int:pk>/edit/", views.news_edit, name="news_edit"),
    path("news/create/", views.news_create, name="news_create"),
    path("news/<int:pk>/delete/", views.news_delete, name="news_delete"),
    path("news/<int:news_id>/add_comment/", views.add_comment, name="add_comment"),
    path("groups_list/",views.GroupListView.as_view(),name="groups_list"),
    path("group/<int:pk>", views.GroupDetailView, name="group"),
    path("groups/invite/<str:username>/<int:pk>/", views.GroupInvite, name="group_invite"),
    path("groups/join/<int:pk>/", views.join_group, name="group_join"),
    path("groups/group_leave/<int:pk>/", views.leave_group, name="group_leave"),
    path("groups/group_kik/<str:username>/<int:pk>/", views.kik_group, name="group_kik"),
    path("groups/group_create/", views.GroupCreateView.as_view(), name="group_create"),
    path("groups/group_update/<int:pk>/",views.GroupUpdateView.as_view(),name="group_update"),
    path("groups/group_delete/<int:pk>/", views.GroupDeleteView.as_view(),name="group_delete"),
    path("reaction/toggle/", views.reaction_toggle, name="reaction_toggle"),
    path("send-message/", views.SendMailView.as_view(), name="send_message"),
    path("mailbox/", views.UserMailView, name="mailbox"),
    path("mailbox/sender_mail", views.sender_mail, name="sender_mail"),
    path("mailbox/recipient_mail", views.recipient_mail, name="recipient_mail"),
    path("mailbox/send_mail", views.send_mail, name="send_mail"),
    path("mailbox/send_mail_parent", views.send_mail_parent, name="send_mail_parent"),
    path("mailbox/message/<int:mail_id>/", views.message_detail, name="message_detail"),
    path("update_status/", views.update_status, name="update_status"),
    path("", include(router.urls)),
]
