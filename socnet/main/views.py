
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.views import View

from .forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages import get_messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView
from rest_framework import status, viewsets
from django.db.models import Count, Q, Prefetch
from rest_framework.decorators import action, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .forms import UpdateUserForm, UpdateProfileForm, AvatarUploadForm, UserPasswordChangeForm, CommentForm
from .models import Profile, Friendship, Comment
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import News, Tag, Reaction
from .serializers import *
from .forms import NewsForm, ReactionForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Case, When, IntegerField, Sum
from django.shortcuts import render

from .forms import LoginUserForm


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

    return render(request, 'main/chat.html', context)




@login_required
def profile_view(request, username):
    '''Просмотр профиля пользователя'''

    # Получение профиля пользователя
    profile = get_object_or_404(Profile, user__username=username)

    # Проверяем, является ли текущий пользователь владельцем профиля
    is_owner = request.user.username == username


    # Проверка уровня конфиденциальности профиля
    privacy_level = profile.privacy

    avatar = profile.media_files.filter(file_type='avatar').last()

    # Определяем, есть ли дружба между текущим пользователем и владельцем профиля
    friendship_exists = (
            Friendship.objects.filter(
                profile_one__user=request.user, profile_two=profile, status__name='Друзья'
            ).exists() or
            Friendship.objects.filter(
                profile_one=profile, profile_two__user=request.user, status__name='Друзья'
            ).exists()
    )


    friends_profiles = []

    if friendship_exists or is_owner is True:
        # Предварительная загрузка аватаров
        avatars_prefetch = Prefetch(
            'media_files',
            queryset=Mediafile.objects.filter(file_type='avatar'),
            to_attr='avatars'
        )

        # Получаем все дружеские связи и загружаем связанные профили, пользователей и аватары
        friendships = Friendship.objects.filter(
            Q(status__name='Друзья') &
            (Q(profile_one=profile) | Q(profile_two=profile))
        ).select_related('profile_one__user', 'profile_two__user').prefetch_related(
            Prefetch('profile_one__media_files', queryset=Mediafile.objects.filter(file_type='avatar'),
                     to_attr='avatars'),
            Prefetch('profile_two__media_files', queryset=Mediafile.objects.filter(file_type='avatar'),
                     to_attr='avatars')
        )

        # Проходим по каждому объекту Friendship и добавляем профиль друга в список
        for friendship in friendships:
            if friendship.profile_one == profile:
                # Если profile — profile_one, добавляем profile_two в список друзей
                friends_profiles.append(friendship.profile_two)
            else:
                # Иначе добавляем profile_one в список друзей
                friends_profiles.append(friendship.profile_one)

    # Убираем дубликаты, если они есть
    friends_profiles = list(set(friends_profiles))

    ban_exists_out = (
            Friendship.objects.filter(
                profile_one__user=request.user, profile_two=profile, status__name='Заблокирован'
            ).exists() )
    ban_exists_in = (
            Friendship.objects.filter(
                profile_one=profile, profile_two__user=request.user, status__name='Заблокирован'
            ).exists()
    )

    # Определяем, есть ли входящий запрос на дружбу
    incoming_friend_requests = Friendship.objects.filter(
        profile_two=request.user.profile,
        status__name='Отправлен запрос'
    )

    # Определяем, кто отправил запрос, если таковой имеется
    friend_request_senders = [
        request.profile_one for request in incoming_friend_requests if request.profile_one
    ]


    # Определяем видимость профиля в зависимости от уровня конфиденциальности и дружбы
    if privacy_level.name == "Никто" and not is_owner:
        context = {
            'profile': {
                'firstname': profile.firstname,
                'lastname': profile.lastname,
              },
            'restricted_view': True,  # Вид ограничен
            'is_owner': is_owner,
            'avatar': avatar,
            'friendship_exists': friendship_exists,
            'friend_request_senders': friend_request_senders,
            'incoming_friend_requests': incoming_friend_requests,
            'ban_exists_out':ban_exists_out,
            'ban_exists_in': ban_exists_in,

        }
    elif privacy_level.name == "Только друзья" and not friendship_exists and not is_owner:
        context = {
            'profile': {
                'firstname': profile.firstname,
                'lastname': profile.lastname,

            },
            'is_owner': is_owner,
            'restricted_view': True,  # Вид ограничен для друзей
            'avatar': avatar,
            'friendship_exists': friendship_exists,
            'friend_request_senders': friend_request_senders,
            'incoming_friend_requests': incoming_friend_requests,
            'ban_exists_out':ban_exists_out,
            'ban_exists_in': ban_exists_in,

        }
    else:
        # Полный доступ к профилю
        context = {
            'profile': profile,
            'is_owner': is_owner,
            'restricted_view': False,  # Полный доступ к профилю
            'avatar': avatar,
            'friendship_exists': friendship_exists,
            'friend_request_senders': friend_request_senders,
            'incoming_friend_requests': incoming_friend_requests,
            'ban_exists_out':ban_exists_out,
            'ban_exists_in': ban_exists_in,
            'friends_profiles': friends_profiles,
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

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Проверка, был ли загружен новый файл
            if request.FILES.get('file'):  # 'file' - имя поля в форме AvatarUploadForm
                if avatar_form.is_valid():
                    # Удалить предыдущий аватар
                    previous_avatar = profile.media_files.filter(file_type='avatar').last()
                    if previous_avatar:
                        previous_avatar.delete()

                    # Сохранить новый аватар
                    avatar = avatar_form.save(commit=False)
                    avatar.profile = profile
                    avatar.file_type = 'avatar'
                    avatar.save()

            messages.success(request, 'Ваш профиль успешно изменен!')
            return redirect('profile', username=request.user.username)

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

class RegisterUser(FormView):
    template_name = 'main/registration.html'
    form_class = RegistrationForm
    success_url = '/'

    def form_valid(self, form):
        # Сохранение пользователя
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Создание профиля для нового пользователя с обязательными полями
        Profile.objects.create(
            user=user,
            firstname=user.first_name,  # Из модели User
            lastname=user.last_name,    # Из модели User
        )

        # Вход пользователя после регистрации
        auth_login(self.request, user)

        # Создание токена для пользователя
        token = Token.objects.create(user=user)
        self.request.session['token'] = token.key

        return super().form_valid(form)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "main/password_change_form.html"


class LoginUser(LoginView):  # логин через класс - проверка на валидность сразу встроена
    form_class = LoginUserForm
    template_name = 'main/login.html'
    extra_context = {'title': 'Авторизация'}

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            auth_login(self.request, user)

            # Получение или создание токена
            token, _ = Token.objects.get_or_create(user=user)
            self.request.session['token'] = token.key

            return super().form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Вы успешно авторизовались!')
        return reverse_lazy('home')


class LogoutUser(View):
    def get(self, request):
        logout(request)
        # request.session.flush()
        messages.success(request, 'Вы успешно вышли из системы!')
        return redirect('home')


def profile_list(request):
    # Получаем все профили
    profile_items = Profile.objects.select_related('user').all()  # Используем select_related для оптимизации запроса

    # Словарь для хранения аватаров по профилям
    avatars = {}

    # Получаем аватары для всех профилей
    avatar_items = Mediafile.objects.filter(file_type='avatar', profile__in=profile_items)

    # Заполняем словарь аватаров
    for avatar in avatar_items:
        avatars[avatar.profile.id] = avatar

    context = {
        'profile_items': profile_items,
        'avatars': avatars,
    }

    return render(request, 'main/profile_list.html', context)


@require_GET
@login_required
def news_list_api(request):
    user = request.user.profile  # Получаем профиль текущего авторизованного пользователя
    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'mine':
        news_items = News.objects.filter(profile=user).order_by('-created_at')
    elif filter_type == 'friends':
        friend_ids = set()
        friendships_as_one = Friendship.objects.filter(profile_one=user.id, status='Друзья')
        for friendship in friendships_as_one:
            friend_ids.add(friendship.profile_two)
        friendships_as_two = Friendship.objects.filter(profile_two=user.id, status='Друзья')
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
    news_item = get_object_or_404(News, pk=pk)

    # Получаем состояние реакции пользователя
    content_type = ContentType.objects.get_for_model(news_item)
    # Получение корневых комментариев (комментариев, у которых нет родителя)
    root_comments = Comment.objects.filter(news=news_item, parent__isnull=True).select_related('author')

    try:
        reaction = Reaction.objects.get(profile=request.user.profile, content_type=content_type, object_id=news_item.id)
        user_reaction = reaction.reaction_type
    except Reaction.DoesNotExist:
        user_reaction = None

    # Рассчитываем рейтинг
    reactions = Reaction.objects.filter(content_type=content_type, object_id=news_item.id)
    total_reactions = reactions.aggregate(
        total_score=Sum(
            Case(
                When(reaction_type='like', then=1),
                When(reaction_type='dislike', then=-1),
                output_field=IntegerField()
            )
        )
    )
    total_score = total_reactions['total_score'] or 0

    context = {
        'news_item': news_item,
        'root_comments': root_comments,
        'is_owner': request.user == news_item.profile.user,
        'user_reaction': user_reaction,
        'total_score': total_score,
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
    news_item = get_object_or_404(News, pk=pk)

    # Очистка существующих тегов перед началом редактирования
    news_item.tags.clear()

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            # form.save_m2m() больше не нужен, так как form.save() уже сохраняет m2m поля при наличии instance
            messages.success(request, 'Новость успешно отредактирована!')
            return redirect('news_detail', pk=news_item.pk)
    else:
        form = NewsForm(instance=news_item)

    context = {
        'form': form,
        'news_item': news_item,
    }
    return render(request, 'main/edit_news.html', context)


@login_required
def news_delete(request, pk):
    news_item = News.objects.get(pk=pk)
    news_item.delete()
    messages.success(request, 'Новость успешно удалена!')
    return redirect('home')




@csrf_exempt
@login_required
def reaction_toggle(request):
    if request.method == 'POST':
        object_id = request.POST.get('object_id')
        reaction_type = request.POST.get('reaction_type')
        user = request.user

        try:
            news_item = News.objects.get(pk=object_id)
            content_type = ContentType.objects.get_for_model(news_item)

            # Получаем существующую реакцию пользователя, если она есть
            reaction, created = Reaction.objects.get_or_create(
                profile=user.profile,
                content_type=content_type,
                object_id=news_item.id,
                defaults={'reaction_type': reaction_type}
            )

            if not created:
                # Если реакция уже есть, проверяем ее тип
                if reaction.reaction_type == reaction_type:
                    # Удаляем реакцию, если пользователь нажал на ту же кнопку
                    reaction.delete()
                    action = 'removed'
                    reaction_type = None
                else:
                    # Обновляем тип реакции
                    reaction.reaction_type = reaction_type
                    reaction.save()
                    action = 'updated'
                # Пересчитываем рейтинг
                total_reactions = Reaction.objects.filter(content_type=content_type, object_id=news_item.id).aggregate(
                    total_score=Sum(
                        Case(
                            When(reaction_type='like', then=1),
                            When(reaction_type='dislike', then=-1),
                            output_field=IntegerField()
                        )
                    )
                )
                total_score = total_reactions['total_score'] or 0
                return JsonResponse({'action': action, 'reaction_type': reaction_type, 'total_score': total_score})
            else:
                # Реакция была создана
                total_reactions = Reaction.objects.filter(content_type=content_type, object_id=news_item.id).aggregate(
                    total_score=Sum(
                        Case(
                            When(reaction_type='like', then=1),
                            When(reaction_type='dislike', then=-1),
                            output_field=IntegerField()
                        )
                    )
                )
                total_score = total_reactions['total_score'] or 0
                return JsonResponse({'action': 'created', 'reaction_type': reaction_type, 'total_score': total_score})

        except News.DoesNotExist:
            return JsonResponse({'error': 'Новость не найдена.'}, status=404)

    return JsonResponse({'error': 'Неверный запрос.'}, status=400)



def add_comment(request, news_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        news_item = News.objects.get(pk=news_id)

        # Логика добавления комментария
        Comment.objects.create(
            news=news_item,
            text=text,
            parent_id=parent_id,
            author=request.user.profile
        )

        # Рендеринг обновленного списка комментариев
        comments_html = render_to_string('main/partial_comments.html', {
            'root_comments': news_item.comments.filter(parent=None)
        })

        return JsonResponse({'comments_html': comments_html})

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
        profile_one = request.user.profile
        profile_two_id = request.data.get('profile_id')

        if not profile_two_id:
            return JsonResponse({'detail': 'Запрос должен содержать ID профиля'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile_two = Profile.objects.get(id=profile_two_id)
        except Profile.DoesNotExist:
            return JsonResponse({'detail': 'Такого пользователя не существует'}, status=status.HTTP_404_NOT_FOUND)

        if Friendship.objects.filter(
                (Q(profile_one=profile_one, profile_two=profile_two) |
                 Q(profile_one=profile_two, profile_two=profile_one)) &
                ~Q(status__name='Заблокирован')  # Добавим условие, чтобы не учитывать заблокированные
        ).exists():
            return JsonResponse({'detail': 'Вы уже друзья или запрос уже отправлен'}, status=status.HTTP_400_BAD_REQUEST)

        friendship_status = FriendshipStatus.objects.get(name='Отправлен запрос')
        friendship = Friendship.objects.create(profile_one=profile_one, profile_two=profile_two,
                                               status=friendship_status)
        # serializer = self.get_serializer(friendship)

        return JsonResponse({'detail': 'Запрос на дружбу отправлен'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='accept-request', url_name='accept-request')
    def accept_request(self, request, pk):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)

            if friendship.profile_two.id != request.user.profile.id:
                return JsonResponse({'detail': 'Только получатель может принять запрос'},
                                    status=status.HTTP_403_FORBIDDEN)

            if friendship.status.name != 'Отправлен запрос':
                return JsonResponse({'detail': 'Невозможно принять запрос. Запрос не найден или уже принят'},
                                    status=status.HTTP_400_BAD_REQUEST)

            friendship.status = FriendshipStatus.objects.get(name='Друзья')
            friendship.save()

            return JsonResponse({'detail': 'Заявка на дружбу принята'}, status=status.HTTP_201_CREATED)

        except Friendship.DoesNotExist:
            return JsonResponse({'detail': 'Запрос дружбы не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='block-people', url_name='block-people')
    def block_user(self, request, pk):
        profile_one = request.user.profile
        profile_two = Profile.objects.get(id=pk)

               # Проверяем наличие дружбы или запроса на дружбу
        existing_friendship = Friendship.objects.filter(
            (Q(profile_one=profile_one, profile_two=profile_two) |
             Q(profile_one=profile_two, profile_two=profile_one)) &
            Q(status__name__in=['Друзья', 'Отправлен запрос'])
        ).first()  # Используем first() для получения первого найденного объекта или None

        if existing_friendship:
            # Удаляем существующую дружбу или запрос на дружбу
            existing_friendship.delete()

        # Создаем запись о блокировке
        friendship_status = FriendshipStatus.objects.get(name='Заблокирован')
        Friendship.objects.create(profile_one=profile_one, profile_two=profile_two, status=friendship_status)

        return JsonResponse({'detail': 'Пользователь заблокирован'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='unblock-people', url_name='unblock-people')
    def unblock_user(self, request, pk):
        profile_one = request.user.profile

        try:
            profile_two = Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            return JsonResponse({'detail': 'Профиль не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем наличие блокировки
        existing_friendship = Friendship.objects.filter(
            profile_one=profile_one,
            profile_two=profile_two,
            status__name='Заблокирован'
        ).first()  # Используем first() для получения первого найденного объекта или None

        if existing_friendship:
            # Удаляем существующую блокировку
            existing_friendship.delete()
            return JsonResponse({'detail': 'Пользователь успешно разблокирован'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Пользователь не найден в списке заблокированных'},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='deny-request', url_name='deny-request')
    def deny_friendship(self, request, pk=None):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)
            profile = request.user.profile

            if friendship.profile_two != profile and friendship.profile_one != profile:
                return JsonResponse({'detail': 'Вы не можете отклонить этот запрос'}, status=status.HTTP_403_FORBIDDEN)

            friendship.delete()
            return JsonResponse({'detail': 'Запрос на дружбу отклонен'}, status=status.HTTP_200_OK)

        except Friendship.DoesNotExist:
            return JsonResponse({'detail': 'Запрос дружбы не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='delete-friend', url_name='delete-friend')
    def delete_friendship(self, request, pk):
        profile_2 = get_object_or_404(Profile, id=pk)


        # Определяем, есть ли дружба между текущим пользователем и владельцем профиля
        friendship_exists = (
                Friendship.objects.filter(
                    profile_one__user=request.user, profile_two=profile_2, status__name='Друзья'
                ).exists() or
                Friendship.objects.filter(
                    profile_one=profile_2, profile_two__user=request.user, status__name='Друзья'
                ).exists()
        )

        if friendship_exists:
            # Попробуем найти и удалить дружбу
            try:
                friendship = Friendship.objects.get(
                    (Q(profile_one__user=request.user, profile_two=profile_2) |
                     Q(profile_one=profile_2, profile_two__user=request.user)),
                    status__name='Друзья'
                )

                # Удаляем объект дружбы
                friendship.delete()

                return JsonResponse({'detail': 'Дружба успешно удалена.'}, status=status.HTTP_200_OK)

            except Friendship.DoesNotExist:
                return JsonResponse({'detail': 'Дружба не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return JsonResponse({'detail': 'Дружба не существует или уже удалена.'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path='list-requests', url_name='list-requests')
    def list_requests(self, request):
        profile = request.user.profile
        incoming_friend_requests = Friendship.objects.filter(profile_two=profile, status__name='Отправлен запрос')
        return render(request, 'main/partials_friend_requests.html', {'incoming_friend_requests': incoming_friend_requests})

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


@login_required
def friends_list_api(request):
    user_profile = request.user.profile

    friendships = Friendship.objects.filter(
        Q(profile_one=user_profile) | Q(profile_two=user_profile) & Q(status__name='Друзья')
    ).select_related('profile_one', 'profile_two', 'status')

    friends = []
    seen_profiles = set()

    for friendship in friendships:
        if friendship.profile_one == user_profile:
            friend = friendship.profile_two
        else:
            friend = friendship.profile_one

        if friend.id not in seen_profiles:
            seen_profiles.add(friend.id)  # Добавляем ID друга в множество

            friends.append({
                'friend_name': f'{friend.firstname} {friend.lastname}',
                'friend_profile_username': friend.user.username,
                'status': friendship.status.name,
            })

    return JsonResponse({'friends': friends}, safe=False)

@login_required
def send_friend_request(request, username):
    '''Отправить запрос на дружбу'''

    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, user__username=username)

    if user_profile == friend_profile:
        messages.error(request, 'Вы не можете отправить запрос на дружбу самому себе!')
        return redirect("profile", username=username)

    if Friendship.objects.filter(
            (Q(profile_one=user_profile) & Q(profile_two=friend_profile)) |
            (Q(profile_one=friend_profile) & Q(profile_two=user_profile))
    ).exists():
        messages.error(request, 'Запрос на дружбу уже отправлен или вы уже друзья.')
        return redirect("profile", username=username)

    sent_status = get_object_or_404(FriendshipStatus, name='Отправлен запрос')

    # Создаем новый объект Friendship с указанным статусом
    Friendship.objects.create(profile_one=user_profile, profile_two=friend_profile, status=sent_status)

    messages.success(request, 'Запрос на дружбу отправлен.')
    return redirect("profile", username=username)


@login_required
def accept_friend_request(request, username):
    '''Принять запрос на дружбу'''

    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, user__username=username)

    friendship = get_object_or_404(Friendship, profile_one=friend_profile, profile_two=user_profile)

    if friendship.status.name == "Друзья":
        messages.error(request, 'Вы уже друзья.')
        return redirect('profile_detail', username=username)
    elif friendship.status.name == "Заблокирован":
        messages.error(request, 'Вы не можете принять этот запрос.')
        return redirect('profile_detail', username=username)
    elif friendship.status.name != "Отправлен запрос":
        messages.error(request, 'Невозможно принять запрос. Некорректный статус запроса.')
        return redirect('profile_detail', username=username)

    # Обновляем статус дружбы на "Друзья"
    friends_status = get_object_or_404(FriendshipStatus, name='Друзья')
    friendship.status = friends_status
    friendship.save()

    messages.success(request, 'Запрос на дружбу принят.')
    return redirect('profile_detail', username=username)

