from django.shortcuts import render

# Create your views here.
def index(request):

    context = {
        'title': 'Домашняя страница',

    }
    return render(request, 'main/index.html', context)


def chat(request):


    context = {
        'key': 112,
        'message': 'Всем приввет',
    }
    return render(request, 'main/chat.html', context)