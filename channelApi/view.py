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
                        stream_keys.append({"name": key.decode('utf-8'),"type": "group"})
                if cursor == 0:
                    break

            while True:
                cursor, keys = r.scan(cursor=cursor, match='*direct*')
                for key in keys:
                    if r.type(key) == b'stream':
                        stream_keys.append({"name": key.decode('utf-8'), "type": "direct"})
                if cursor == 0:
                    break

            return Response({"success": True,
                             "channels": stream_keys})