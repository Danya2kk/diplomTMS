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
