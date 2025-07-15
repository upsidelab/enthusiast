import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


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
        handlers = {
            "start": self.handle_start,
            "stream": self.handle_stream,
            "end": self.handle_end,
            "message_created": self.handle_message_created,
            "action": self.handle_action,
            "error": self.handle_error,
        }

        handler = handlers.get(event_type)
        if handler:
            await handler(event)

    async def handle_start(self, event):
        await self.send(json.dumps({"event": "on_parser_start", "data": {"run_id": event.get("run_id")}}))

    async def handle_stream(self, event):
        await self.send(json.dumps({"event": "on_parser_stream", "data": {"chunk": event.get("token")}}))

    async def handle_end(self, event):
        output = event.get("output")
        await self.send(json.dumps({"event": "on_parser_end", "data": {"output": output}}))
        await self.save_message(output)

    async def handle_message_created(self, event):
        await self.send(json.dumps({"event": "message_id", "data": {"output": event.get("answer_id")}}))

    async def handle_action(self, event):
        await self.send(json.dumps({"event": "action", "data": {"output": event.get("output")}}))

    async def handle_error(self, event):
        await self.send(json.dumps({"event": "error", "data": {"output": event.get("output")}}))

    async def save_message(self, output):
        from .models import Conversation, Message

        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        message = Message(conversation=conversation, content=output, sender="system")
        await database_sync_to_async(message.save)()
