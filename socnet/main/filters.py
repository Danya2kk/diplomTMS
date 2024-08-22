from django_filters import rest_framework as filters
from .models import Friendship


class FriendshipFilter(filters.FilterSet):
    status = filters.ChoiseFilter(Friendship.STATUS_CHOICES)

    class Meta:
        model = Friendship
        fields = ['status']