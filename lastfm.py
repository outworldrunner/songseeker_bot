import pylast

from conf import configuration

network = pylast.LastFMNetwork(api_key=configuration['LASTFM']['api_key'],
                               api_secret=configuration['LASTFM']['api_secret'],
                               username=configuration['LASTFM']['username'],
                               password_hash=pylast.md5(configuration['LASTFM']['password']))


def get_similar_artist(artist, amount=5):
    artist = network.get_artist(artist)

    similars = artist.get_similar()
    for similar in similars[:amount]:
        if str(artist).lower() not in str(similar.item).lower():
            yield str(similar.item)


def get_similar_track(artist, track, amount=5):
    track = network.get_track(artist, track)

    similars = track.get_similar()
    print(similars)
    for similar in similars[:amount]:
        yield str(similar.item)