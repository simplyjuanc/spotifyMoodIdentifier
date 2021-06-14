import os
from re import M
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

    auth_response = requests.get(AUTH_URL, data=payload)

    # response_url = urlparse.urlparse(auth_response.url)   
    # print(response_url)
    


    # session['code'] = auth_response_data['code']
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
    
    return str(session.items())


@main.route('/trackhistory')
def obtainTrackHistory():
    call_url = BASE_URL + 'me/player/recently-played'
    token = session.get('access_token')
    print(session.keys())

    header = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept':'application/json',
        'Content-Type': 'application/json'
        }

    data = {
        'limit':50
    }

    response = requests.get(call_url, headers=header, params=data)
    response_json = response.text
    response_json = json.loads(response.text)

    tracks = {}
    for track in response_json['items']:
        track_name = track['track']['name']
        tracks[track_name] = {'id':track['track']['id']}

    session['TRACK_HISTORY'] = tracks
    session.modified = True
    return 'I have saved session variable for tracks history.' #+ str(tracks)


@main.route('/trackanalysis')
def analyseTracks():
    analysis_url = BASE_URL + 'audio-analysis/'
    feats_url = BASE_URL + 'audio-features'
    tracks = session.get('TRACK_HISTORY', None)

    # print(tracks)

    track_id_list = []
    for k,v in tracks.items():
        track_id_list.append(v['id'])
    
    track_id_str = ','.join(track_id_list)
    response = requests.get(feats_url, headers=header, params=track_id_str)
    

    # print(response)

    return 'Correctly finished processing audio analysis and saved in session dict variable' 

@main.route('/tracktraits')
def averageTrackTraits():
    pass

@main.route('/visualisetraits')
def visualiseTrackTraits():
    pass

@main.route('/sess1')
def session1():
    return session.sid

@main.route('/sess2')
def session2():
    return session.sid


