import os
from flask import Flask, redirect, request, session
from requests.api import head
from flask_session import Session
import requests, json
import urllib.parse

main = Flask(__name__)

main.secret_key = os.urandom(24).hex()
main.config['SESSION_TYPE'] = 'filesystem'
Session(main)

BASE_URL = 'https://api.spotify.com/v1/'
REDIRECT_URI = 'http://localhost:5000/redirect'
SCOPES = 'user-read-recently-played'



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

    session['access_token'] = token_json['access_token']
    session.modified = True
    session['refresh_token'] = token_json['refresh_token']
    session.modified = True
    
    return 'Access and refresh tokens have been saved.'


@main.route('/trackhistory')
def getTrackHistory():
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
        tracks.append({
            'id':track_id,
            'name':track_name
        })
        

    session['TRACK_HISTORY'] = tracks
    session.modified = True
    return 'I have saved session variable for tracks history.' #+ str(tracks)


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
    print(track_info_list)
    
    index = 0
    for track in track_info_list:
        if track['id'] == tracks[index]['id']:
            track['name'] = tracks[index]['name']
        else:
            print('Error at {}'.format(track))
        index += 1
    
    session['TRACK_ANALYSis'] = track_info_list

    return 'Sucess'


@main.route('/visualisetraits')
def visualiseTrackTraits():
    pass
