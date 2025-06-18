from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import redis
import json
import threading

r = redis.Redis(host='192.168.201.40', port=6379, db=0)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_name = "chat:direct"
        await self.accept()

        # Start Redis pub/sub listening in a thread
        threading.Thread(target=self.listen_to_redis, daemon=True).start()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        if message:
            # Send to live subscribers
            r.publish(self.channel_name, message)

            # Persist in stream
            r.xadd(self.channel_name, {"message": message})

    def listen_to_redis(self):
        pubsub = r.pubsub()
        pubsub.subscribe(self.channel_name)
        for message in pubsub.listen():
            if message['type'] == 'message':
                asyncio.run(self.send_to_socket(message['data']))

    async def send_to_socket(self, message):
        await self.send(text_data=json.dumps({
            'message': message.decode('utf-8')
        }))
