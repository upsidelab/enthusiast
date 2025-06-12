import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from agent.models import Message
from agent.models import Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"conversation_{self.conversation_id}"

        # Join the conversation group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_message(self, event):
        event_type = event.get("event")
        if event_type == "start":
            await self.send(text_data=json.dumps({"event": "on_parser_start", "data": {"run_id": event.get("run_id")}}))
        elif event_type == "stream":
            # Forward the token to the client
            await self.send(text_data=json.dumps({"event": "on_parser_stream", "data": {"chunk": event.get("token")}}))
        elif event_type == "end":
            output = event.get("output")
            await self.send(text_data=json.dumps({"event": "on_parser_end", "data": {"output": output}}))
            # Save the streamed response to the database
            await self.save_message(output)
        elif event_type == "message_created":
            output = event.get("answer_id")
            await self.send(text_data=json.dumps({"event": "message_id", "data": {"output": output}}))

    async def save_message(self, output):
        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        message = Message(conversation=conversation, content=output, sender="system")
        await database_sync_to_async(message.save)()
