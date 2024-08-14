from django.contrib.sites import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
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
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return Response({
                'refresh': str(refresh),
                'access': str(access)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer