from django_filters import rest_framework as filters
from .models import *


class FriendshipFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(choices=Friendship.STATUS_CHOICES)
    profile_one = filters.NumberFilter(field_name='profile_one', lookup_expr='exact')
    profile_two = filters.NumberFilter(field_name='profile_two', lookup_expr='exact')

    class Meta:
        model = Friendship
        fields = ['status', 'profile_one', 'profile_two']


class ProfileFilter(filters.FilterSet):
    firstname = filters.CharFilter(field_name='firstname', lookup_expr='icontains')
    lastname = filters.CharFilter(field_name='lastname', lookup_expr='icontains')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    interests = filters.MultipleChoiceFilter(
        field_name='interests',
        queryset = Interest.objects.all(),
    )

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'location', 'interests']

class GroupFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='name', lookup_expr='icontains')
    group_type = filters.MultipleChoiceFilter(field_name='group_type', choices=Group.GROUP_TYPES)

    class Meta:
        model = Group
        fields = ['name', 'description', 'group_type']