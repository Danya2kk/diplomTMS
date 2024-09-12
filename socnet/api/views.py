from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import ProfileSerializer, ActivityLogSerializer, GroupSerializer, FriendshipSerializer, \
    NotificationSerializer
from main.models import Profile, Friendship, ActivityLog, Group, Notification, FriendshipStatus


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=["get"])
    def get_online_friends(self, request):
        try:
            profile = request.user.profile

            friends_ids = Friendship.objects.filter(
                Q(profile_one=profile) | Q(profile_two=profile), status="friends"
            ).values_list("profile_one", "profile_two")

            friends = set(
                friend for friend_list in friends_ids for friend in friend_list
            )
            friends.remove(profile.id)

            friends_online = Profile.objects.filter(
                id__in=friends_ids, status_profile__is_online=True
            )

            serializer = self.get_serializer(friends_online, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {"detail": "Профиль пользователя не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"])
    def get_reccomended_friends(self, request):
        try:
            profile = request.user.profile
            user_interests = profile.interests.values_list("id", flat=True)

            recomended_profiles = Profile.objects.exclude(id=profile.id).annotate(
                interests_count=Count(
                    "interests", filter=Q(interests__in=user_interests)
                ).order_by("-interests_count")
            )

            serializer = self.get_serializer(recomended_profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(
                {"detail": "Профиль пользователя не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all().order_by("-timestamp")
    serializer_class = ActivityLogSerializer

    @action(detail=False, methods=["get"])
    def recent(self, request):
        profile = request.user.profile
        activity_type = request.query_params.get("type", None)

        activities = ActivityLog.objects.filter(profile=profile)

        if activity_type:
            activities = activities.filter(action_type=activity_type)

        activities = activities.order_by("-timestamp")[:10]

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=["post"])
    def invite(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        if request.user.profile != group.creator:
            return Response(
                {"detail": "Только создатель группы может отправлять приглашения"},
                status=status.HTTP_403_FORBIDDEN,
            )

        invited_ids = request.data.get("profile_ids", [])
        if not invited_ids:
            return Response(
                {"detail": "Не указаны профили для приглашения"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invited_profiles = Profile.objects.filter(id__in=invited_ids)

        for profile in invited_profiles:
            Notification.objects.create(
                profile=profile,
                notification_type=Notification.GROUP_INVITE,
                content=f"Вы получили инвайт в группу'{group.name}'",
            )

        return Response(f"Инвайт отправлен {len(invited_profiles)} пользователям")


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @action(detail=False, methods=["post"])
    def send_request(self, request):
        profile_one = request.user.profile
        profile_two_id = request.data.get("profile_id")

        if not profile_two_id:
            return Response(
                {"detail": "Запрос должен содержать ID профиля"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile_two = Profile.objects.get(id=profile_two_id)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Такого пользователя не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Friendship.objects.filter(
            (
                Q(profile_one=profile_one, profile_two=profile_two)
                | Q(profile_one=profile_two, profile_two=profile_one)
            )
            & ~Q(
                status__name="Заблокирован"
            )  # Добавим условие, чтобы не учитывать заблокированные
        ).exists():
            return Response(
                {"detail": "Вы уже друзья или запрос уже отправлен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friendship_status = FriendshipStatus.objects.get(name="Отправлен запрос")
        friendship = Friendship.objects.create(
            profile_one=profile_one, profile_two=profile_two, status=friendship_status
        )


        return JsonResponse(
            {"detail": "Запрос на дружбу отправлен"}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="accept-request",
        url_name="accept-request",
    )
    def accept_request(self, request, pk):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)

            if friendship.profile_two.id != request.user.profile.id:
                return JsonResponse(
                    {"detail": "Только получатель может принять запрос"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if friendship.status.name != "Отправлен запрос":
                return JsonResponse(
                    {
                        "detail": "Невозможно принять запрос. Запрос не найден или уже принят"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            friendship.status = FriendshipStatus.objects.get(name="Друзья")
            friendship.save()


            return JsonResponse(
                {"detail": "Заявка на дружбу принята"}, status=status.HTTP_201_CREATED
            )
        except Friendship.DoesNotExist:
            return JsonResponse(
                {"detail": "Запрос дружбы не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True, methods=["post"], url_path="block-people", url_name="block-people"
    )
    def block_user(self, request, pk):
        profile_one = request.user.profile
        profile_two = Profile.objects.get(id=pk)

        # Проверяем наличие дружбы или запроса на дружбу
        existing_friendship = Friendship.objects.filter(
            (
                Q(profile_one=profile_one, profile_two=profile_two)
                | Q(profile_one=profile_two, profile_two=profile_one)
            )
            & Q(status__name__in=["Друзья", "Отправлен запрос"])
        ).first()  # Используем first() для получения первого найденного объекта или None

        if existing_friendship:
            # Удаляем существующую дружбу или запрос на дружбу
            existing_friendship.delete()

        # Создаем запись о блокировке
        friendship_status = FriendshipStatus.objects.get(name="Заблокирован")
        Friendship.objects.create(
            profile_one=profile_one, profile_two=profile_two, status=friendship_status
        )


        return JsonResponse(
            {"detail": "Пользователь заблокирован"}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="unblock-people",
        url_name="unblock-people",
    )
    def unblock_user(self, request, pk):
        profile_one = request.user.profile

        try:
            profile_two = Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие блокировки
        existing_friendship = Friendship.objects.filter(
            profile_one=profile_one,
            profile_two=profile_two,
            status__name="Заблокирован",
        ).first()  # Используем first() для получения первого найденного объекта или None

        if existing_friendship:
            # Удаляем существующую блокировку
            existing_friendship.delete()


            return JsonResponse(
                {"detail": "Пользователь успешно разблокирован"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Пользователь не найден в списке заблокированных"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        detail=True, methods=["post"], url_path="deny-request", url_name="deny-request"
    )
    def deny_friendship(self, request, pk=None):
        try:
            friendship = get_object_or_404(Friendship, pk=pk)
            profile = request.user.profile

            if friendship.profile_two != profile and friendship.profile_one != profile:
                return Response(
                    {"detail": "Вы не можете отклонить этот запрос"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            friendship.delete()



            return JsonResponse(
                {"detail": "Запрос на дружбу отклонен"}, status=status.HTTP_200_OK
            )

        except Friendship.DoesNotExist:
            return JsonResponse(
                {"detail": "Запрос дружбы не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="delete-friend",
        url_name="delete-friend",
    )
    def delete_friendship(self, request, pk):
        profile_2 = get_object_or_404(Profile, id=pk)

        # Определяем, есть ли дружба между текущим пользователем и владельцем профиля
        friendship_exists = (
            Friendship.objects.filter(
                profile_one__user=request.user,
                profile_two=profile_2,
                status__name="Друзья",
            ).exists()
            or Friendship.objects.filter(
                profile_one=profile_2,
                profile_two__user=request.user,
                status__name="Друзья",
            ).exists()
        )

        if friendship_exists:
            # Попробуем найти и удалить дружбу
            try:
                friendship = Friendship.objects.get(
                    (
                        Q(profile_one__user=request.user, profile_two=profile_2)
                        | Q(profile_one=profile_2, profile_two__user=request.user)
                    ),
                    status__name="Друзья",
                )

                # Удаляем объект дружбы
                friendship.delete()


                return Response(
                    {"detail": "Дружба успешно удалена."}, status=status.HTTP_200_OK
                )

            except Friendship.DoesNotExist:
                return Response(
                    {"detail": "Дружба не найдена."}, status=status.HTTP_404_NOT_FOUND
                )

        else:
            return JsonResponse(
                {"detail": "Дружба не существует или уже удалена."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-timestamp")
    serializer_class = NotificationSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Notification.objects.filter(profile=profile).order_by("-timestamp")

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk)

        if notification.profile != request.user.profile.id:
            Response(
                {"detail": "Уведомление не принадлежит вам"},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification.read = True
        notification.save()
        return Response(
            {"detail": "Уведомление помечено как прочитанное"},
            status=status.HTTP_200_OK,
        )