from django import forms
from .models import User
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile, User, Mediafile, Comment, Interest, PrivacyLevel
from .models import News, Tag, Reaction
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    firstname = forms.CharField(max_length=255)
    lastname = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'firstname', 'lastname']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid login or password.")
        return cleaned_data


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username']


class UpdateProfileForm(forms.ModelForm):
    firstname = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя', 'class': 'form-input'})
    )
    lastname = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'placeholder': 'Введите фамилию', 'class': 'form-input'})
    )
    age = forms.IntegerField(
        label='Возраст',
        widget=forms.NumberInput(attrs={'placeholder': 'Введите возраст', 'class': 'form-input'}),
        required=False,
    )
    gender = forms.CharField(
        label='Пол',
        widget=forms.TextInput(attrs={'placeholder': 'Введите пол', 'class': 'form-input'}),
        required=False,
    )
    location = forms.CharField(
        label='Местонахождение',
        widget=forms.TextInput(attrs={'placeholder': 'Введите местонахождение', 'class': 'form-input'}),
        required=False,
    )
    link = forms.CharField(
        label='Ссылка на другие профили',
        widget=forms.TextInput(attrs={'placeholder': 'Введите ссылку на другие профили', 'class': 'form-input'}),
        required=False,
    )
    settings = forms.CharField(
        label='Настройки',
        widget=forms.TextInput(attrs={'placeholder': 'Введите настройки', 'class': 'form-input'}),
        required=False,
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        label='Интересы',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),  # Чекбоксы для множественного выбора
        required=False
    )
    privacy = forms.ModelChoiceField(
        queryset=PrivacyLevel.objects.all(),
        label='Уровень приватности',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'age', 'gender', 'location', 'link', 'settings', 'privacy', 'interests']


class AvatarUploadForm(forms.ModelForm):

    file = forms.ImageField(
        label='Аватар',  # Метка для поля file
        required=False  # Поле не обязательно
    )
    # file = forms.FileField(required=False)

    class Meta:
        model = Mediafile
        fields = ['file']


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class NewsForm(forms.ModelForm):
    title = forms.CharField(
        label='Название',  # Метка для поля title
        widget=forms.TextInput(attrs={'placeholder': 'Введите название новости'})
    )
    content = forms.CharField(
        label='Содержание',  # Метка для поля content
        widget=forms.Textarea(attrs={'placeholder': 'Введите содержание новости'})
    )
    image = forms.ImageField(
        label='Изображение',  # Метка для поля image
        required=False  # Поле не обязательно
    )
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=Tag.objects.all(),
    #     label='Тэги',  # Метка для поля tags
    #     # widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # Можно добавить класс или другие атрибуты
    #     widget=forms.SelectMultiple(),
    #     required=False
    # )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label='Тэги',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),  # Чекбоксы для множественного выбора
        required=False
    )

    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'tags']  # Добавьте все нужные поля

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     # Устанавливаем значение по умолчанию для поля `tags`
    #     if not self.instance.pk:  # Если объект ещё не сохранен (новый объект)
    #         first_tag = Tag.objects.first()
    #         if first_tag:
    #             self.fields['tags'].initial = [first_tag]  # Список значений по умолчанию


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']  # Включить поле 'parent' для поддержки ответов
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'parent': forms.HiddenInput()  # Скрыть поле 'parent' в форме
        }


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

