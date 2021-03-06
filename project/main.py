import os
from flask import Flask, redirect, request, session
from flask_session import Session
import requests, json
from urllib.parse import urlparse, parse_qs

# if __name__ == '__main__':
main = Flask(__name__)
# main.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
# main.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
main.secret_key = os.urandom(24).hex()
main.config['SESSION_TYPE'] = 'filesystem'
Session(main)

BASE_URL = 'https://api.spotify.com/v1/'
REDIRECT_URI = 'http://localhost:5000/redirect'
SCOPES = 'user-read-recently-played'

# header = {
#     # 'Authorization': 'Bearer {}'.format(session['token_data']['access_token']),
#     'Accept':'application/json',
#     'Content-Type': 'application/json'
#     }


@main.route('/authorise')
def getAccessToken():
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    payload = {
        'client_id':os.getenv('CLIENT_ID'),
        'response_type':'code',
        'redirect_uri':REDIRECT_URI,
        'scope':SCOPES,
    }

    requests.get(AUTH_URL, data=payload)

    return redirect('/redirect')



@main.route('/redirect')
def getAuthCode():
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type':'authorization_code',
        'code':request.args['code'],
        'redirect_uri':REDIRECT_URI,
        'client_id':os.getenv('CLIENT_ID'),
        'client_secret':os.getenv('SECRET_KEY')
    } 
    token_response = requests.post(TOKEN_URL, data=data)
    token_json = json.loads(token_response.text)
    # print(token_json)
    session['access_token'] = token_json['access_token']
    session.modified = True
    session['refresh_token'] = token_json['refresh_token']
    session.modified = True
    
    return redirect('/trackhistory')


@main.route('/trackhistory')
def obtainTrackHistory():
    call_url = BASE_URL + 'me/player/recently-played'
    token = session.get('access_token')

    header = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept':'application/json',
        'Content-Type': 'application/json'
        }

    data = {
        'limit':50
    }

    response = requests.get(call_url, headers=header, params=data)
    response_json = json.loads(response.text)

    tracks = []
    for track in response_json['items']:
        track_id = track['track']['id']
        track_name = track['track']['name']
        artist_id = track['track']['artists'][0]['id']

        tracks.append({
            'id':track_id,
            'name':track_name,
            'artist_id': artist_id,
        })
        
    session['TRACK_HISTORY'] = tracks
    session.modified = True
    return redirect('/trackanalysis')

# Run the different tracks through the analysis endpoint, and save the averages of the audio features and the ids of the latest tracks and artists
@main.route('/trackanalysis')
def analyseTracks():
    feats_url = BASE_URL + 'audio-features'
    tracks = session.get('TRACK_HISTORY', None)
    token = session.get('access_token')

    header = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept':'application/json',
        'Content-Type': 'application/json'
    }

    track_id_list = []
    for i in tracks:
        track_id_list.append(i['id'])
    
    track_id_str = ','.join(track_id_list)
    params = {
        'ids':track_id_str
    }
    
    _response = requests.get(feats_url, headers=header, params=params)
    _response_json = json.loads(_response.text)
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


@main.route('/visualisetraits')
def visualiseTrackTraits():
    pass

@main.route('/sess1')
def session1():
    return session.sid

@main.route('/sess2')
def session2():
    return session.sid


