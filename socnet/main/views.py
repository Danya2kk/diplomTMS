from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from .forms import UpdateUserForm, UpdateProfileForm, AvatarUploadForm, UserPasswordChangeForm
from .models import Profile


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
