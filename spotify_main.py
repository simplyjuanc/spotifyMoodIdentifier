import os
import json
import requests
from flask import Flask, session, redirect

from spotify_client import SpotifyClient
from spotify_auth import auth_bp


main = Flask(__name__)
main.secret_key = os.urandom(64).hex()
main.config['SESSION_TYPE'] = 'filesystem'
main.config['SESSION_COOKIE_NAME'] = 'tests'
main.register_blueprint(auth_bp)

client = SpotifyClient()

def call_api(self, endpoint, method='GET', params=None, payload=None):
    """
    Calls Spotify API with ACCESS_TOKEN, return JSON object for analysis.
    """
    call_url = self.BASE_URL + endpoint
    access_token = self.getAccessToken()
    print(access_token)

    header = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Accept':'application/json',
        'Content-Type': 'application/json'
    }

    if method == 'GET':
        response = requests.get(call_url, headers=header, data=payload, params=params)
    elif method == 'POST':
        response = requests.post(call_url, headers=header, data=payload, params=params)
    else:
        print('Please use either GET or POST methods.')
    
    return dict(json.loads(response.text))

@main.route('/trackhistory')
def obtainTrackHistoryUrl():
    return client.obtainTrackHistory()

@main.route('/trackanalysis')
def analyseTracks():
    
    tracks = session.get('TRACK_HISTORY', None)

    track_id_list = []
    for i in tracks:
        track_id_list.append(i['id'])
    
    track_id_str = ','.join(track_id_list)
    params = {
        'ids':track_id_str
    }
    
    _response_json = client.call_api(endpoint='audio_features', params=params)

    track_info_list = _response_json['audio_features']

    audioFeatures = {
        'danceability':0,
        'energy':0,
        'loudness':0,
        'mode':0,
        'speechiness':0,
        'acousticness':0,
        'instrumentalness':0,
        'liveness':0,
        'valence':0,
        'tempo':0
    }


    # Loop creates seed tracks from the first 10 tracks, alternating artist and song id
    # It uses the audio feautures of all the tracks in history, not only the first 10
    artist_ids = []
    track_ids = []
    for i in range(len(tracks)):
        if i < 10:
            if i % 2 == 0:
                artist_ids.append(tracks[i]['artist_id'])
            if i % 2 == 1:
                track_ids.append(tracks[i]['id'])
        for k,v in audioFeatures.items():
            if k in track_info_list[i].keys():
                audioFeatures[k] = track_info_list[i][k] + v

    for k, v in audioFeatures.items():
        audioFeatures[k] = v / len(track_info_list)
        
    audioFeatures['artist_ids'] = artist_ids
    audioFeatures['tack_ids'] = track_ids
    session['AUDIO_FEATURES'] = audioFeatures
    session.modified = True
    return audioFeatures
