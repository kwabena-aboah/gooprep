import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LessonStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lesson_id = self.scope['url_route']['kwargs']['lesson_id']
        self.group = f"lesson_{self.lesson_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def lesson_status_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
