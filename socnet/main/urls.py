from django.urls import path
from . import views
from .views import StatusListView,StatusCreateView,StatusDeleteView,StatusUpdateView,StatusDetailView

app_name = 'main'
app_name1 = 'tags'
app_name2 = 'comments'
app_name3 = 'reactions'

urlpatterns = [
    path('', StatusListView.as_view(), name='status-list'),
    path('create/', StatusCreateView.as_view(), name='status-create'),
    path('<int:pk>/', StatusDetailView.as_view(), name='status-detail'),
    path('<int:pk>/update/', StatusUpdateView.as_view(), name='status-update'),
    path('<int:pk>/delete/', StatusDeleteView.as_view(), name='status-delete'),
    path('', views.GroupListView.as_view(), name='group-list'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/join/', views.join_group, name='join-group'),
    path('<int:pk>/leave/', views.leave_group, name='leave-group'),
    path('create/', views.GroupCreateView.as_view(), name='group-create'),
    path('<int:pk>/update/', views.GroupUpdateView.as_view(), name='group-update'),
    path('<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group-delete'),
    path('search/', views.group_search, name='group-search'),
    path('', views.FriendshipListView.as_view(), name='friendship-list'),
    path('<int:pk>/', views.FriendshipDetailView.as_view(), name='friendship-detail'),
    path('create/', views.FriendshipCreateView.as_view(), name='friendship-create'),
    path('<int:pk>/update/', views.FriendshipUpdateView.as_view(), name='friendship-update'),
    path('<int:pk>/delete/', views.FriendshipDeleteView.as_view(), name='friendship-delete'),
    path('<int:pk>/accept/', views.accept_friendship, name='friendship-accept'),
    path('<int:pk>/reject/', views.reject_friendship, name='friendship-reject'),
    path('<int:pk>/block/', views.block_friendship, name='friendship-block'),
    path('<int:pk>/unblock/', views.unblock_friendship, name='friendship-unblock'),
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('create/', views.news_create, name='news_create'),
    path('<int:pk>/delete/', views.news_delete, name='news_delete'),
    path('tags/', views.tag_list, name='tag_list'),
    path('<int:pk>/', views.tag_detail, name='tag_detail'),
    path('create/', views.create_tag, name='create_tag'),
    path('<int:pk>/edit/', views.edit_tag, name='edit_tag'),
    path('<int:pk>/delete/', views.delete_tag, name='delete_tag'),
    path('<int:news_pk>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:comment_pk>/edit/', views.comment_edit, name='comment_edit'),
    path('<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:content_type_id>/<int:object_id>/<str:reaction_type>/create/', views.reaction_create, name='reaction_create'),
    path('<int:content_type_id>/<int:object_id>/count/', views.reaction_count, name='reaction_count'),
]
