import requests
import json
from conf import configuration
import string
import random

def recognition_audio(voice):
    data = {
        'return': 'timecode,apple_music,deezer,spotify',
        'api_token': configuration['AUD']['token']
    }
    result = requests.post('https://api.audd.io/', data=data, files={'file': voice})
    print(result.json())
    if result.json()['result'] is None:
        return None, None
    if 'deezer' in result.json()['result']:
        id_track = result.json()['result']['deezer']['id']
    elif 'spotify' in result.json()['result']:
        id_track = result.json()['result']['spotify']['id']
    elif 'apple_music' in result.json()['result']:
        id_track = result.json()['result']['apple_music']['playParams']['id']
    else:
        id_track = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
    audio = result.json()
    if audio['status'] == "success":
        artist = audio['result']['artist']
        title = audio['result']['title']
    else:
        return None, id_track
    return f"{artist} - {title}", id_track