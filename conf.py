import json
import redis

with open("conf.json", "r") as f:
    configuration = json.loads(f.read())


r = redis.StrictRedis(host="127.0.0.1",
                        port=6379,
                        db=0)
