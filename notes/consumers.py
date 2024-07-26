import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("sync_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sync_group", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle incoming data and broadcast to group
        await self.channel_layer.group_send(
            "sync_group",
            {
                "type": "sync.message",
                "message": data["message"],
            }
        )

    async def sync_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
