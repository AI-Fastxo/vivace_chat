from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import redis

class RedisChannelListView(APIView):
        def post(self, request):
            r = redis.Redis(host='192.168.201.40', port=6379, db=0)

            id_chats = [str(i) for i in request.data.get("id_chat", [])]
            print("🧠 Lista recibida de idChatRoomList:", id_chats)
            cursor = 0
            stream_keys = []

            while True:
                cursor, keys = r.scan(cursor=cursor, match='*group*')
                for key in keys:
                    if r.type(key) == b'stream':
                        short = key.decode('utf-8').split(':')[0]
                        idchat = key.decode('utf-8').split(':')[3].split('_')[1]
                        print("🧠 De grupos el id es:", idchat)

                        if idchat in id_chats:
                            stream_keys.append({
                                "idChat": idchat,
                                "name": key.decode('utf-8'),
                                "type": "group",
                                "short": short,
                            })
                if cursor == 0:
                    break

            while True:
                cursor, keys = r.scan(cursor=cursor, match='*direct*')
                for key in keys:
                    if r.type(key) == b'stream':
                        short = key.decode('utf-8').split(':')[0]
                        stream_keys.append({
                            "name": key.decode('utf-8'),
                            "type": "direct",
                            "short": short,
                        })
                if cursor == 0:
                    break

            return Response({"success": True,
                             "channels": stream_keys})
class RedisChannelMessagesView(APIView):
    def get(self, request, chatFullId):
        r = redis.Redis(host='192.168.201.40', port=6379, db=0)
        messages = r.xrevrange(chatFullId)

        parsed_messages = []
        for msg_id, data in messages:
            stream_id = msg_id.decode('utf-8')
            epoch_ms = stream_id.split('-')[0]
            parsed_messages.append({
                "id_redis": stream_id,
                "name": chatFullId,
                "message": data.get(b"message", b"").decode('utf-8'),
                "idSender": data.get(b"userId", b"").decode('utf-8'),
                "senderFullname": data.get(b"fullname", b"").decode('utf-8'),
                "mention": data.get(b"mention", b"").decode('utf-8'),
                "timestamp": int(epoch_ms)
            })

            # Sort descending by timestamp (epoch)
            parsed_messages.sort(key=lambda msg: msg['timestamp'], reverse=False)

        return Response({
            "success": True,
            "channel": chatFullId,
            "messages": parsed_messages
        })

    def post(self, request, idUserMentioned):
        r = redis.Redis(host='192.168.201.40', port=6379, db=0)

        # 🔧 Leer nombres de stream desde el body
        chats_name = [str(i) for i in request.data.get("chats_name", [])]
        print("🧠 Lista recibida de chats_name:", chats_name)

        result = []

        for chatFullId in chats_name:
            messages = r.xrevrange(chatFullId)
            short = chatFullId.split(':')[0]
            print("🧠 Short del fullId:", short)
            for msg_id, data in messages:
                mention = data.get(b"mention", b"").decode('utf-8')
                if mention != idUserMentioned:
                    continue  # Saltar mensajes que no mencionan al usuario

                result.append({
                    "id_redis": msg_id.decode('utf-8'),
                    "name": chatFullId,
                    "short": short,
                    "type": chatFullId.split(':')[1],
                    "message": data.get(b"message", b"").decode('utf-8'),
                    "idSender": data.get(b"userId", b"").decode('utf-8'),
                    "senderFullname": data.get(b"fullname", b"").decode('utf-8'),
                    "timestamp": int(msg_id.decode('utf-8').split('-')[0]),
                    "mention": mention,
                })

        return Response({
            "success": True,
            "mention": idUserMentioned,
            "messages": result
        })

