from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import UpdateUserForm, UpdateProfileForm
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
    profile = get_object_or_404(Profile, user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'main/profile.html', context)


@login_required
def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    context = {
        'profile': profile,
    }
    return render(request, 'main/profile.html', context)


@login_required
def update_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно изменен!')
            return redirect('profile', username)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    }

    return render(request, 'main/profile_update.html', context)