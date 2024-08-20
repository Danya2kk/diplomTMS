from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import Profile, User, Mediafile
from .models import News, Tag, Comment, Reaction
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username']


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'age', 'gender', 'location', 'link', 'settings', 'privacy', 'interests']

    labels = {
        'firstname': 'Имя',
        'lastname': 'Фамилия',
        'age': 'Возраст',
        'gender': 'Пол',
        'location': 'Местоположение',
        'link': 'Ссылки',
        'settings': 'Настройки',
        'privacy': 'Конфиденциальность',
        'interests': 'Интересы'
    }

    widgets = {
        'firstname': forms.TextInput(attrs={'class': 'form-input'}),
        'lastname': forms.TextInput(attrs={'class': 'form-input'}),
        'age': forms.TextInput(attrs={'class': 'form-input'}),
        'gender': forms.TextInput(attrs={'class': 'form-input'}),
        'location': forms.TextInput(attrs={'class': 'form-input'}),
        'link': forms.TextInput(attrs={'class': 'form-input'}),
        'settings': forms.TextInput(attrs={'class': 'form-input'}),
        'privacy': forms.TextInput(attrs={'class': 'form-input'}),
        'interests': forms.TextInput(attrs={'class': 'form-input'}),
    }


class AvatarUploadForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = Mediafile
        fields = ['file']


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ['reaction_type']
        widgets = {
            'reaction_type': forms.RadioSelect,
        }

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        # так делать правильнее чем через поля формы т.к страхует при изменения модели юзера
        model = get_user_model()
        fields = ['username', 'password']
