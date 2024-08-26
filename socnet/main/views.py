from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .forms import UpdateUserForm, UpdateProfileForm, AvatarUploadForm, UserPasswordChangeForm
from .models import Profile, Friendship
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import News, Tag, Comment, Reaction
from .forms import NewsForm, CommentForm, ReactionForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_GET
from rest_framework import viewsets, filters, status
from .serializers import *
from .forms import LoginUserForm
from django.db.models import Q, Count
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.
def index(request):
    context = {
        'title': 'Домашняя страница',

    }
    return render(request, 'main/index.html', context)


def chat(request):
    context = {
        'is_chat_page': 'true'
    }
    return render(request, 'main/chat.html', context)


@login_required
def my_profile_view(request):
    '''Просмотр своего профиля'''

    profile = get_object_or_404(Profile, user=request.user)

    context = {
        'profile': profile,
        'is_owner': True,  # Устанавливаем, что текущий пользователь — владелец профиля
    }

    return render(request, 'main/profile.html', context)


@login_required
def profile_view(request, username):
    '''Просмотр публичного профиля'''

    # Если текущий пользователь пытается получить доступ к своему же профилю
    if request.user.username == username:
        return redirect('my_profile')

    profile = get_object_or_404(Profile, user__username=username)
    privacy_level = profile.privacy

    if privacy_level.name == "Никто" and profile.user != request.user:
        context = {
            'profile': {
                'firstname': profile.firstname,
                'lastname': profile.lastname,
            },
            'restricted_view': True,  # Указываем, что вид ограничен
            'is_owner': profile.user == request.user,
        }
    elif privacy_level.name == "Только друзья" and profile.user not in request.user.friends:
        '''Надо разобраться с моделью Friendship'''

        context = {
            'profile': {
                'firstname': profile.firstname,
                'lastname': profile.lastname,
            },
            'is_owner': profile.user == request.user,
            'restricted_view': True

        }
    else:
        context = {
            'profile': profile,
            'is_owner': profile.user == request.user,
            'restricted_view': False
        }
    return render(request, 'main/profile.html', context)


@login_required
def update_profile(request):
    '''Редактирование профиля'''

    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        avatar_form = AvatarUploadForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid() and avatar_form.is_valid():
            user_form.save()
            profile_form.save()

            avatar = avatar_form.save(commit=False)
            avatar.profile = profile
            avatar.file_type = 'image'
            avatar.save()

            messages.success(request, 'Ваш профиль успешно изменен!')
            return redirect('my_profile')

    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=profile)
        avatar_form = AvatarUploadForm()

    # Получаем последний загруженный аватар
    avatar = profile.media_files.filter(file_type='image').last()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'avatar': avatar,
        'avatar_form': avatar_form,
    }

    return render(request, 'main/profile_update.html', context)


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "main/password_change_form.html"


class LoginUser(LoginView):  # логин через класс - проверка на валидность сразу встроена
    form_class = LoginUserForm
    template_name = 'main/login.html'
    extra_context = {'title': 'Авторизация'}

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно авторизовались!')
        return reverse_lazy('home')


@login_required
def news_list(request):
    news_items = News.objects.all().order_by('-created_at')
    context = {
        'news_items': news_items,
    }
    return render(request, 'main/news_list.html', context)


@require_GET
@login_required
def news_list_api(request):
    user = request.user.profile  # Получаем профиль текущего авторизованного пользователя
    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'mine':
        news_items = News.objects.filter(profile=user).order_by('-created_at')
    elif filter_type == 'friends':
        friend_ids = set()
        friendships_as_one = Friendship.objects.filter(profile_one=user.id, status='friends')
        for friendship in friendships_as_one:
            friend_ids.add(friendship.profile_two)
        friendships_as_two = Friendship.objects.filter(profile_two=user.id, status='friends')
        for friendship in friendships_as_two:
            friend_ids.add(friendship.profile_one)
        news_items = News.objects.filter(profile_id__in=friend_ids).order_by('-created_at')
    else:  # filter_type == 'all'
        news_items = News.objects.all().order_by('-created_at')

    # Преобразуем данные в формат JSON, добавляя полный путь к изображению
    data = [
        {
            'id': item.id,
            'title': item.title,
            'image': request.build_absolute_uri(item.image.url) if item.image else ''
        }
        for item in news_items
    ]
    return JsonResponse(data, safe=False)


@login_required
def news_detail(request, pk):
    # Получение объекта новости или выдача 404 ошибки, если объект не найден
    news_item = get_object_or_404(News, pk=pk)

    # Проверка, что текущий пользователь является владельцем новости
    is_owner = news_item.profile.user == request.user

    context = {
        'news_item': news_item,
        'is_owner': is_owner,  # Используем более понятное имя переменной
    }

    return render(request, 'main/news_detail.html', context)


@login_required
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            # Получаем профиль текущего пользователя
            try:
                profile = Profile.objects.get(user=request.user)
                news_item.profile = profile
            except Profile.DoesNotExist:
                # Обработка случая, если профиль не найден
                return redirect('home')  # Убедитесь, что `some_error_page` определена в вашем маршруте

            news_item.save()

            # Сохраняем теги, если они были выбраны
            form.save_m2m()  # Сохранение ManyToMany полей
            messages.success(request, 'Новость успешно добавлена!')
            return redirect('home')
    else:
        form = NewsForm()

    context = {
        'form': form,
    }
    return render(request, 'main/create_news.html', context)


@login_required
def news_edit(request, pk):
    news_item = News.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            form.save_m2m()  # Сохранение ManyToMany полей
            messages.success(request, 'Новость успешно отредактирована!')
            return redirect('news_detail', pk=news_item.pk)
    else:
        form = NewsForm(instance=news_item)
        print(form.initial['tags'])
    context = {
        'form': form,
        'news_item': news_item,
    }
    return render(request, 'main/edit_news.html', context)


@login_required
def news_delete(request, pk):
    news_item = News.objects.get(pk=pk)
    if request.method == 'POST':
        news_item.delete()
        return redirect('news_list')
    context = {
        'news_item': news_item,
    }
    return render(request, 'main/delete_news.html', context)


@login_required
def comment_create(request, news_pk):
    news_item = get_object_or_404(News, pk=news_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user.profile
            comment.news = news_item
            comment.save()
            return redirect('news_detail', pk=news_item.pk)
        else:
            form = CommentForm()
        context = {'form': form, 'news_item': news_item}
        return render(request, 'comment_create.html', context)


@login_required
def comment_edit(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user.profile != comment.author:
        return redirect('news_detail', pk=comment.news.pk)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('news_detail', pk=comment.news.pk)
        else:
            form = CommentForm(instance=comment)
        context = {'form': form, 'comment': comment}
        return render(request, 'comment_edit.html', context)


LIKE = 'like'
DISLIKE = 'dislike'
HEART = 'heart'

REACTION_CHOICES = [
    (LIKE, 'Like'),
    (DISLIKE, 'Dislike'),
    (HEART, 'Heart'),
]


@login_required
def reaction_create(request, content_type_id, object_id, reaction_type):
    content_type = ContentType.objects.get(pk=content_type_id)
    obj = content_type.get_object_for_this_type(pk=object_id)
    if request.method == 'POST':
        try:
            reaction = Reaction.objects.get(
                profile=request.user.profile,
                content_type=content_type,
                object_id=object_id,
                reaction_type=reaction_type
            )
            reaction.delete()
            response_data = {'status': 'removed'}
        except Reaction.DoesNotExist:
            Reaction.objects.create(
                profile=request.user.profile,
                content_type=content_type,
                object_id=object_id,
                reaction_type=reaction_type
            )
            response_data = {'status': 'added'}
        return JsonResponse(response_data)
    else:
        form = ReactionForm(initial={'reaction_type': reaction_type})
        context = {'form': form, 'obj': obj}
        return render(request, 'reactions/reaction_form.html', context)


@login_required
def reaction_count(request, content_type_id, object_id):
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.get_object_for_this_type(pk=object_id)
    reaction_counts = {
        reaction_type: Reaction.objects.filter(
            content_type=content_type,
            object_id=object_id,
            reaction_type=reaction_type
        ).count()
        for reaction_type in REACTION_CHOICES
    }
    return JsonResponse(reaction_counts)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['get'])
    def get_online_friends(self, request):
        try:
            profile = request.user.profile

            friends_ids = Friendship.objects.filter(
                Q(profile_one=profile) | Q(profile_two=profile),
                status='friends'
            ).values_list('profile_one', 'profile_two')

            friends = set(friend for friend_list in friends_ids for friend in friend_list)
            friends.remove(profile.id)

            friends_online = Profile.objects.filter(id__in=friends_ids, status_profile__is_online=True)

            serializer = self.get_serializer(friends_online, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'detail': 'Профиль пользователя не найден'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=False, methods=['get'])
    def get_reccomended_friends(self, request):
        try:
            profile = request.user.profile
            user_interests = profile.interests.values_list('id', flat=True)

            recomended_profiles = Profile.objects.exclude(id=profile.id).annotate(
            interests_count=Count('interests', filter=Q(interests__in=user_interests))
            .order_by('-interests_count')
            )

            serializer = self.get_serializer(recomended_profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'detail': 'Профиль пользователя не найден'}, status=status.HTTP_404_NOT_FOUND)
class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all().order_by('-timestamp')
    serializer_class = ActivityLogSerializer

    @action(detail=False, methods=["get"])
    def recent(self, request):
        profile = request.user.profile
        activity_type = request.query_params.get('type', None)

        activities = ActivityLog.objects.filter(profile=profile)

        if activity_type:
            activities = activities.filter(action_type=activity_type)

        activities = activities.order_by('-timestamp')[:10]

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['post'])
    def invite(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        if request.user.profile != group.creator:
            return Response({'detail': 'Только создатель группы может отправлять приглашения'}, status=status.HTTP_403_FORBIDDEN)

        invited_ids = request.data.get('profile_ids', [])
        if not invited_ids:
            return Response({'detail': 'Не указаны профили для приглашения'}, status=status.HTTP_400_BAD_REQUEST)

        invited_profiles = Profile.objects.filter(id__in=invited_ids)

        for profile in invited_profiles:
            Notification.objects.create(profile=profile, notification_type=Notification.GROUP_INVITE,
                content=f"Вы получили инвайт в группу'{group.name}'")

        return Response(f'Инвайт отправлен {len(invited_profiles)} пользователям')

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @action(detail=False, methods=['post'])
    def send_request(self, request):
        profile_one = request.user.profile.id
        profile_two_id = request.data.get('profile_id')

        if not profile_two_id:
            return Response({'detail': 'Запрос должен быть отправлен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile_two = Profile.objects.get(id=profile_two_id)
        except Profile.DoesNotExist():
            return Response({'detail': 'Такого пользователя не существует'}, status=status.HTTP_404_NOT_FOUND)

        if Friendship.objects.filter(
            (Q(profile_one=profile_one) & Q(profile_two=profile_two)) |
            (Q(profile_one=profile_two) & Q(profile_two=profile_one))
        ).exists():
            return Response({'detail': 'Вы уже друзья'}, status=status.HTTP_400_BAD_REQUEST)

        friendship = Friendship.objects.create(profile_one=profile_one, profile_two=profile_two.id)
        serializer = self.get_serializer(friendship)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept_request(self, request, pk):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)

            if friendship.profile_two != request.user.profile.id:
                return Response({'detail': 'Только получатель может принять запрос'}, status=status.HTTP_403_FORBIDDEN)

            if friendship.status != 'sent':
                return Response({'detail': 'Невозможно принять запрос. Запрос не найден или уже принят'}, status=status.HTTP_400_BAD_REQUEST)

            friendship.status = 'friends'
            friendship.save()
            return Response({'detail': 'Заявка на дружбу принята'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            return Response({'detail': 'Запрос дружбы не найден'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['post'])
    def block_user(self, request, pk):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)

            friendship.status = 'blocked'
            friendship.save()

            return Response({'detail': 'Пользователь заблокирован'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            return Response({'detail': 'Запрос дружбы не найден'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['post'])
    def deny_friendship(self, request, pk):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)
            profile = request.user.profile

            if friendship.profile_two != profile.id or friendship.profile_one != profile.id:
                return Response({'detail': 'Нужно быть другом пользователя'}, status=status.HTTP_403_FORBIDDEN)

            if profile.id == friendship.profile_one:
                friendship.profile_one = friendship.profile_two
                friendship.profile_two = profile.id

            friendship.status = 'sent'
            friendship.save()

            return Response({'detail': 'Пользователь удален из друзей'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            return Response({'detail': 'Запрос дружбы не найден'}, status=status.HTTP_404_NOT_FOUND)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-timestamp')
    serializer_class = NotificationSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Notification.objects.filter(profile=profile).order_by('-timestamp')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk)

        if notification.profile != request.user.profile.id:
            Response({'detail': 'Уведомление не принадлежит вам'}, status=status.HTTP_403_FORBIDDEN)

        notification.read = True
        notification.save()
        return Response({'detail': 'Уведомление помечено как прочитанное'}, status=status.HTTP_200_OK)
