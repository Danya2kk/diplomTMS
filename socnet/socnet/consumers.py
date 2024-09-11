import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        print(f"Connecting to room: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Загружаем все сообщения группы за текущий день
        await self.load_messages()

    async def disconnect(self, close_code):
        print(f"Disconnected from room: {self.room_group_name}")

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Received message: {text_data}")

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]

        # Получаем имя пользователя асинхронно
        firstname, lastname = await self.get_user_profile(user)

        # Сохраняем сообщение в базе данных
        await self.save_message(message, user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': firstname,
                'lastname': lastname
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        lastname = event['lastname']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'lastname': lastname
        }))

    async def load_messages(self):
        now = datetime.now()
        today = now.date()

        # Используем sync_to_async для вызова синхронной операции
        messages = await sync_to_async(self.get_messages)(self.room_name, today)

        for message in messages:
            await self.send(text_data=json.dumps({
                'message': message['messages'],
                'username': message['profile__firstname'],
                'lastname': message['profile__lastname']
            }))

    def get_messages(self, room_name, today):
        from main.models import Chat  # Импортируем модель внутри функции
        return list(Chat.objects.filter(
            group_id=room_name,
            created_at__date=today
        ).values('messages', 'profile__firstname', 'profile__lastname'))

    async def save_message(self, message, user):
        from main.models import Chat  # Импортируем модель внутри функции
        await sync_to_async(Chat.objects.create)(
            messages=message,
            profile=user.profile,
            group_id=self.room_name
        )

    async def get_user_profile(self, user):
        """Асинхронно получаем имя и фамилию пользователя."""
        profile = await sync_to_async(lambda: user.profile)()
        return profile.firstname, profile.lastname
