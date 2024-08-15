from django.shortcuts import render, get_object_or_404

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


def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    context = {
        'profile': profile,
    }
    return render(request, 'main/profile.html', context)