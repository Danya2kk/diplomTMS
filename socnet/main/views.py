from django.contrib.sites import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from .serializers import UserSerializer, AuthTokenSerializer


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


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(View):
    def get(self, request):
        return render(request, 'registration.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post('http://127.0.0.1:8000/api/register/', data={'username': username, 'password': password})

        if response.status_code == 201:
            token = response.json().get('token')
            return HttpResponse(f"Registration successful! Token: {token}")
        return HttpResponse(f"Registration failed: {response.json()}", status=400)

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post('http://127.0.0.1:8000/api/login/', data={'username': username, 'password': password})

        if response.status_code == 200:
            token = response.json().get('token')
            return HttpResponse(f"Login successful! Token: {token}")
        return HttpResponse(f"Login failed: {response.json()}", status=400)