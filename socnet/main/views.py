from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import login, authenticate, get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
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

User = get_user_model()
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)


            token = Token.objects.create(user=user)
            request.session['token'] = token.key

            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)


                token, _ = Token.objects.get_or_create(user=user)
                request.session['token'] = token.key

                return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')