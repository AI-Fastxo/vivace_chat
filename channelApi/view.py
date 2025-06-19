from rest_framework.views import APIView
from rest_framework.response import Response
import redis

class RedisChannelListView(APIView):
        def get(self, request):
            r = redis.Redis(host='192.168.201.40', port=6379, db=0)
            cursor = 0
            stream_keys = []

            while True:
                cursor, keys = r.scan(cursor=cursor, match='*group*')
                for key in keys:
                    if r.type(key) == b'stream':
                        short = key.decode('utf-8').split(':')[0]
                        stream_keys.append({
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
                "id": stream_id,
                "message": data.get(b"message", b"").decode('utf-8'),
                "idSender": data.get(b"userId", b"").decode('utf-8'),
                "senderFullname": data.get(b"fullname", b"").decode('utf-8'),
                "timestamp": int(epoch_ms)
            })

            # Sort descending by timestamp (epoch)
            parsed_messages.sort(key=lambda msg: msg['timestamp'], reverse=False)

        return Response({
            "success": True,
            "channel": chatFullId,
            "messages": parsed_messages
        })