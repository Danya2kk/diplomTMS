import sys

from io import BytesIO
from PIL import Image

from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms


from .models import (Comment, Friendship, Group, Interest, Mail, Mediafile,
                     News, PrivacyLevel, Profile, Reaction, Tag, User)


class RegistrationForm(forms.ModelForm):
    ''' Форма для регистрации пользователей'''

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Введите пароль", "class": "form-input"}
        ),
    )
    password_confirm = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Повторите пароль", "class": "form-input"}
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(
                attrs={"placeholder": "Введите логин", "class": "form-input"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Введите email", "class": "form-input"}
            ),
            "first_name": forms.TextInput(
                attrs={"placeholder": "Введите имя", "class": "form-input"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Введите фамилию", "class": "form-input"}
            ),
        }
        labels = {
            "username": "Логин",
            "email": "Email",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def clean(self):

        #Функция для проверки что пароли совпадают
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Пароли не совпадают")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(
            self.cleaned_data["password"]
        )  # Устанавливаем зашифрованный пароль
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    ''' Форма для авторизации пользователея'''


    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        # метод для проверки пароля

        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid login or password.")
        return cleaned_data


class UpdateUserForm(forms.ModelForm):
    '''Смена username пользователя'''

    username = forms.CharField(
        required=True,
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    class Meta:
        model = User
        fields = ["username"]


class UpdateProfileForm(forms.ModelForm):
    '''Форма для редактирования профиля'''

    firstname = forms.CharField(
        label="Имя",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите имя", "class": "form-input"}
        ),
    )
    lastname = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите фамилию", "class": "form-input"}
        ),
    )
    age = forms.IntegerField(
        label="Возраст",
        widget=forms.NumberInput(
            attrs={"placeholder": "Введите возраст", "class": "form-input"}
        ),
        required=False,
    )
    gender = forms.CharField(
        label="Пол",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите пол", "class": "form-input"}
        ),
        required=False,
    )
    location = forms.CharField(
        label="Местонахождение",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите местонахождение", "class": "form-input"}
        ),
        required=False,
    )
    link = forms.CharField(
        label="Ссылка на другие профили",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введите ссылку на другие профили",
                "class": "form-input",
            }
        ),
        required=False,
    )
    settings = forms.CharField(
        label="Настройки",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите настройки", "class": "form-input"}
        ),
        required=False,
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        label="Интересы",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-checkbox"}
        ),  # Чекбоксы для множественного выбора
        required=False,
    )
    privacy = forms.ModelChoiceField(
        queryset=PrivacyLevel.objects.all(),
        label="Уровень приватности",
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "firstname",
            "lastname",
            "age",
            "gender",
            "location",
            "link",
            "settings",
            "privacy",
            "interests",
        ]

class AvatarUploadForm(forms.ModelForm):
    '''Форма для загрузки аватара'''


    file = forms.ImageField(label="Аватар", required=False)

    class Meta:
        model = Mediafile
        fields = ["file"]

    def save(self, profile=None, *args, **kwargs):
        avatar = super().save(commit=False)

        # Установим профиль, если он передан
        if profile:
            avatar.profile = profile

        # Если изображение загружено
        if self.cleaned_data.get("file"):
            image = self.cleaned_data["file"]
            img = Image.open(image)

            # Приведение изображения к размеру 300x300 пикселей
            img = img.resize((250, 250), Image.Resampling.LANCZOS)

            # Преобразование изображения обратно в файл для сохранения
            output = BytesIO()
            img.save(output, format="JPEG", quality=90)
            output.seek(0)

            # Создаем новое изображение для сохранения в модели
            avatar.file = InMemoryUploadedFile(
                output,
                "ImageField",
                f"{image.name.split('.')[0]}.jpg",
                "image/jpeg",
                sys.getsizeof(output),
                None,
            )

        avatar.save()
        return avatar


class MediaUploadForm(forms.ModelForm):
    '''Форма для загрузки медиафайлов'''

    file = forms.ImageField(
        label="Фотография",
        # required=False
    )

    class Meta:
        model = Mediafile
        fields = ["file"]


class UserPasswordChangeForm(PasswordChangeForm):
    '''Форма для смены пароля'''

    old_password = forms.CharField(
        label="Старый пароль", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    new_password1 = forms.CharField(
        label="Новый пароль", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    new_password2 = forms.CharField(
        label="Повторить пароль",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )


class NewsForm(forms.ModelForm):
    ''' Форма для создания/редактирования новости'''

    title = forms.CharField(
        label="Название",  # Метка для поля title
        widget=forms.TextInput(attrs={"placeholder": "Введите название новости"}),
    )
    content = forms.CharField(
        label="Содержание",  # Метка для поля content
        widget=forms.Textarea(attrs={"placeholder": "Введите содержание новости"}),
    )
    image = forms.ImageField(
        label="Изображение",  # Метка для поля image
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label="Тэги",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-checkbox"}
        ),  # Чекбоксы для множественного выбора
        required=False,
    )

    class Meta:
        model = News
        fields = ["title", "content", "image", "tags"]

    def save(self, *args, **kwargs):
        news = super().save(commit=False)

        # Метод для обьрезки изображения.Если изображение загружено
        if self.cleaned_data.get("image"):
            image = self.cleaned_data["image"]
            img = Image.open(image)

            # Приведение изображения к размеру
            img = img.resize((250, 250), Image.Resampling.LANCZOS)

            # Преобразование изображения обратно в файл для сохранения
            output = BytesIO()
            img.save(output, format="JPEG", quality=90)  # Сохраняем с качеством 90%
            output.seek(0)

            # Создаем новое изображение для сохранения в модели
            news.image = InMemoryUploadedFile(
                output,
                "ImageField",
                f"{image.name.split('.')[0]}.jpg",
                "image/jpeg",
                sys.getsizeof(output),
                None,
            )

        news.save()
        return news



class CommentForm(forms.ModelForm):
    ''' Форма для создания комментария'''


    class Meta:
        model = Comment
        fields = ["text", "parent"]  # Включить поле 'parent' для поддержки ответов
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "parent": forms.HiddenInput(),  # Скрыть поле 'parent' в форме
        }


class ReactionForm(forms.ModelForm):
    ''' Форма для отставления реакции'''

    class Meta:
        model = Reaction
        fields = ["reaction_type"]
        widgets = {
            "reaction_type": forms.RadioSelect,
        }


class LoginUserForm(AuthenticationForm):
    ''' Форма для авторизации пользователей'''

    username = forms.CharField(
        label="Логин", widget=forms.TextInput(attrs={"class": "form-input"})
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-input"})
    )

    class Meta:
        # так делать правильнее чем через поля формы т.к страхует при изменения модели юзера
        model = get_user_model()
        fields = ["username", "password"]


class MailForm(forms.ModelForm):
    ''' Форма для отправки почты'''

    class Meta:
        model = Mail
        fields = [
            "recipient",
            "content",
            "parent",
        ]  # 'parent' для возможности ответа на сообщение
        widgets = {
            "content": forms.Textarea(attrs={"placeholder": "Введите сообщение..."}),
        }


class FriendshipCreateForm(forms.ModelForm):
    ''' Форма для создания дружюы'''

    class Meta:
        model = Friendship
        fields = ["profile_two", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_two"].queryset = Profile.objects.exclude(
            user=self.instance.profile_one.user
        )


class FriendshipUpdateForm(forms.ModelForm):
    ''' Форма для обновления дружбы'''

    class Meta:
        model = Friendship
        fields = ["status", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class FriendshipSearchForm(forms.Form):
    ''' Форма для поиска дружбы'''

    search_term = forms.CharField(label="Поиск", required=False)


class GroupCreateForm(forms.ModelForm):
    ''' Форма для создания группы'''

    name = forms.CharField(
        label="Название",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите название группы", "class": "form-input"}
        ),
    )
    description = forms.CharField(
        label="Описание группы",
        widget=forms.Textarea(
            attrs={"placeholder": "Введите описание группы", "class": "form-input"}
        ),
    )

    group_type = forms.ChoiceField(
        label="Тип группы",
        choices=Group.GROUP_TYPES,
        widget=forms.Select(
            attrs={"class": "form-checkbox"}
        ),  # Чекбоксы для множественного выбора
    )
    photo = forms.ImageField(
        label="Изображение",  # Метка для поля image
    )

    rules = forms.CharField(
        label="Правила группы",
        widget=forms.Textarea(
            attrs={"placeholder": "Укажите правила группы", "class": "form-input"}
        ),
    )

    class Meta:
        model = Group
        fields = ["name", "description", "photo", "group_type", "rules"]

    def save(self, *args, **kwargs):
        group = super().save(commit=False)

        # Метод обрезки изобрадения. Если изображение загружено
        if self.cleaned_data.get("photo"):
            image = self.cleaned_data["photo"]
            img = Image.open(image)

            # Приведение изображения к размеру 500x500 пикселей
            img = img.resize((250, 250), Image.Resampling.LANCZOS)

            # Преобразование изображения обратно в файл для сохранения
            output = BytesIO()
            img.save(output, format="JPEG", quality=90)  # Сохраняем с качеством 90%
            output.seek(0)

            # Создаем новое изображение для сохранения в модели
            group.photo = InMemoryUploadedFile(
                output,
                "ImageField",
                f"{image.name.split('.')[0]}.jpg",
                "image/jpeg",
                sys.getsizeof(output),
                None,
            )

        group.save()
        return group


class GroupUpdateForm(forms.ModelForm):
    ''' Форма для обновления группы'''

    class Meta:
        model = Group
        fields = ["name", "description", "photo", "group_type", "rules"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "rules": forms.Textarea(attrs={"rows": 3}),
            # 'group_type': forms.Select(choices=GROUP_TYPES),
        }


class GroupSearchForm(forms.Form):
    ''' Форма для поиска группы'''

    search_term = forms.CharField(label="Поиск", required=False)
