from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path
from main import views
from django.contrib.auth.views import LogoutView

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
    path('news/<int:news_id>/add_comment/', views.add_comment, name='add_comment'),
    # path('<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    # path('reaction/<int:object_id>/<str:model_name>/<str:reaction_type>/', views.add_reaction, name='add_reaction'),
    path('reaction/toggle/', views.reaction_toggle, name='reaction_toggle'),
    # path('<int:content_type_id>/<int:object_id>/count/', views.reaction_count, name='reaction_count'),

]
