from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import redis
import json
import threading

from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import redis
import json
import threading

r = redis.Redis(host='192.168.201.40', port=6379, db=0)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pubsub = None
        self._stop_listening = False

    async def connect(self):
        self.chat_name = self.scope["url_route"]["kwargs"]["chatName"]
        self.channel_name = self.chat_name  # Redis channel name

        await self.accept()

        # Start Redis pub/sub listening in a thread
        threading.Thread(target=self.listen_to_redis, daemon=True).start()

    async def disconnect(self, close_code):
        self._stop_listening = True  # Signal the listener loop to stop
        if self.pubsub:
            try:
                self.pubsub.unsubscribe()
                self.pubsub.close()
            except Exception as e:
                print(f"[Redis] Error during cleanup: {e}")
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        sender = data.get("sender")
        idSender = data.get("senderId")
        idUserMention = data.get("mention")

        if message:
            redis_entry = {
                "message": message,
                "fullname": sender or "Unknown",
                "userId": idSender or "Unknown",
                "mention": idUserMention or "",
            }

            # Send live via pub/sub
            r.publish(self.channel_name, json.dumps(redis_entry))

            r.publish("notifications", json.dumps({
                "chat": self.chat_name,
                "short": self.chat_name.split(':')[0],
                "sender": sender,
                "userId": idSender,
                "mention": idUserMention,
                "message": message,
                "type": "new_message"
            }))

            # Persist full structure in stream
            r.xadd(self.channel_name, redis_entry)

    async def send_to_socket(self, message):
        parsed = json.loads(message.decode('utf-8'))
        await self.send(text_data=json.dumps(parsed))

    def listen_to_redis(self):
        try:
            self.pubsub = r.pubsub()
            self.pubsub.subscribe(self.channel_name)

            for message in self.pubsub.listen():
                if self._stop_listening:
                    break
                if message['type'] == 'message':
                    asyncio.run(self.send_to_socket(message['data']))
        except Exception as e:
            print(f"[Redis] Listener error: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pubsub = None
        self._stop_listening = False

    async def connect(self):
        self.channel_name = "notifications"  # canal global de notificaciones
        await self.accept()
        threading.Thread(target=self.listen_to_redis, daemon=True).start()
        print("CONECTADO DESDE LOGIN PARA NOTIFICACIONES")

    async def disconnect(self, close_code):
        self._stop_listening = True
        if self.pubsub:
            try:
                self.pubsub.unsubscribe()
                self.pubsub.close()
            except Exception as e:
                print(f"[Redis] Cleanup error: {e}")
        await self.close()

    async def send_to_socket(self, message):
        parsed = json.loads(message.decode("utf-8"))
        await self.send(text_data=json.dumps(parsed))

    def listen_to_redis(self):
        try:
            self.pubsub = r.pubsub()
            self.pubsub.subscribe("notifications")  # <- escucha este canal

            for message in self.pubsub.listen():
                if self._stop_listening:
                    break
                if message["type"] == "message":
                    asyncio.run(self.send_to_socket(message["data"]))
        except Exception as e:
            print(f"[Redis] Listener error: {e}")


