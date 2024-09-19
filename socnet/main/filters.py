from django_filters import rest_framework as filters
from django_filters import DateFilter
from .models import *


class FriendshipFilter(filters.FilterSet):
    '''
    Фильтр дружбы
    '''

    status = filters.ModelChoiceFilter(queryset=FriendshipStatus.objects.all())
    profile_one = filters.ModelChoiceFilter(field_name='profile_one', queryset=Profile.objects.all())
    profile_two = filters.ModelChoiceFilter(field_name='profile_two', queryset=Profile.objects.all())

    class Meta:
        model = Friendship
        fields = ['status', 'profile_one', 'profile_two']


class ProfileFilter(filters.FilterSet):
    '''
    Фильтр профиля
    '''

    firstname = filters.CharFilter(field_name='firstname', lookup_expr='icontains', label='Имя')
    lastname = filters.CharFilter(field_name='lastname', lookup_expr='icontains', label='Фамилия')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains', label='Местоположение')
    gender = filters.CharFilter(field_name='gender', lookup_expr='icontains', label='Пол')
    interests = filters.ModelMultipleChoiceFilter(
        field_name='interests',
        queryset=Interest.objects.all(),
     label = 'Интересы'
    )

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'gender', 'location', 'interests']

class GroupFilter(filters.FilterSet):
    '''
    Фильтр группы
    '''

    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='Название')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains', label='Описание')
    group_type = filters.ChoiceFilter(field_name='group_type', choices=Group.GROUP_TYPES, label='Тип группы')

    class Meta:
        model = Group
        fields = ['name', 'description', 'group_type']

class NewsFilter(filters.FilterSet):
    '''
    Фильтр новостей
    '''

    title = filters.CharFilter(field_name='title', lookup_expr='icontains', label='Название новости')
    content = filters.CharFilter(field_name='content', lookup_expr='icontains', label='Текст новости')
    created_at = DateFilter(field_name='created_at', lookup_expr='gte', label='Дата создания позже:')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Tag.objects.all(),
        label='Тэги'
    )
    class Meta:
        model = News
        fields = ['title', 'content', 'created_at', 'tags']
