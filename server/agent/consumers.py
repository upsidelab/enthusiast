import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f"conversation_{self.conversation_id}"

        # Join the conversation group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected for conversation {self.conversation_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_token(self, event):
        token = event["token"]
        # Forward the token to the client
        await self.send(text_data=json.dumps({
            "event": "on_parser_stream",
            "data": {"chunk": token}
        }))