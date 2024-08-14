from django.shortcuts import render

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user_role = request.user.role
    else:
        user_role = 'гость'

    context = {
        'title': 'Домашняя страница',
        'user_role': user_role,
    }
    return render(request, 'main/index.html', context)


def chat(request):


    context = {
        'key': 112,
        'message': 'Всем приввет',
    }
    return render(request, 'main/chat.html', context)