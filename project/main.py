import requests, json

from flask import Blueprint
from flask.globals import session

from . import auth


main = Blueprint('main', __name__)

BASE_URL = 'https://api.spotify.com/v1/'
header = {
    'Authorization': 'Bearer {}'.format(session.get('token_data', None)),
    'Accept':'application/json',
    'Content-Type': 'application/json'
    }

@main.route('/trackhistory')
def obtainTrackHistory():
    call_url = BASE_URL + 'me/player/recently-played'
    
    # header = {
    #     'Authorization': 'Bearer ' + session['token_data']['access_token'],
    #     'Accept':'application/json',
    #     'Content-Type': 'application/json'
    #     }

    data = {
        'limit':50
    }

    response = requests.get(call_url, headers=header, params=data)
    # response_json = response.text
    response_json = json.loads(response.text)

    tracks = {}
    for track in response_json['items']:
        track_name = track['track']['name']
        tracks[track_name] = {'id':track['track']['id']}

    session['TRACK_HISTORY'] = tracks

    return 'I have saved session variable for tracks history.\n\n' + str(tracks)


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

