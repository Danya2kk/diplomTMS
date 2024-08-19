from django.urls import path
from main import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.LoginUser.as_view(), name='login'),     # для
    path('logout', LogoutView.as_view(), name='logout'),
    path('chat', views.chat, name='chat'),
    path('news/<int:pk>', views.news_detail, name='news_detail'),
    path('news', views.news_list, name='news'),
    path('api/news/', views.news_list_api, name='news_list_api'),
    path('<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('create/', views.news_create, name='news_create'),
    path('<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('tags/', views.tag_list, name='tag_list'),
    path('<int:news_pk>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:comment_pk>/edit/', views.comment_edit, name='comment_edit'),
    # path('<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:content_type_id>/<int:object_id>/<str:reaction_type>/create/', views.reaction_create,
         name='reaction_create'),
    path('<int:content_type_id>/<int:object_id>/count/', views.reaction_count, name='reaction_count'),

]
