
from main.models import Profile, Friendship, Group, GroupMembership, Mediafile, Comment, Reaction, News, ActivityLog
from main.models import Status, Notification
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели профиля
    '''
    class Meta:
        model = Profile
        fields = "__all__"

class FriendshipSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели дружбы
    '''
    class Meta:
        model = Friendship
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели группы
    '''
    class Meta:
        model = Group
        fields = "__all__"

class GroupMembershipSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для участника группы
    '''

    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    class Meta:
        model = GroupMembership
        fields = ['profile', 'group', 'status', 'joined_at']

class MediafileSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели медиа
    '''
    class Meta:
        model = Mediafile
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели комментарий
    '''
    class Meta:
        model = Comment
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели реакции
    '''
    class Meta:
        model = Reaction
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели новостей
    '''
    class Meta:
        model = News
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели лога активности
    '''
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'profile', 'action_type', 'action_type_display', 'description', 'timestamp']
        read_only_fields = ['timestamp', 'profile']


class NotificationSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели уведомления
    '''
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'profile', 'notification_type', 'content', 'timestamp', 'read']