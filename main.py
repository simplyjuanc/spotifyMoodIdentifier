import os
from auth import SECRET_KEY
from flask import Flask, session
from werkzeug.utils import redirect

import spotify_auth as sa

main = Flask(__name__)
main.register_blueprint(sa.auth_blueprint)
main.secret_key = os.urandom(64).hex()
main.config['SESSION_TYPE'] = 'filesystem'
main.config['SESSION_COOKIE_NAME'] = 'tests'

@main.route('/trackhistory')
def obtainTrackHistory():
    _response_json = sa.call_api(endpoint='me/player/recently-played',payload={'limit':50})
    
    tracks = []
    for track in _response_json['items']:
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
    
    tracks = session.get('TRACK_HISTORY', None)

    track_id_list = []
    for i in tracks:
        track_id_list.append(i['id'])
    
    track_id_str = ','.join(track_id_list)
    params = {
        'ids':track_id_str
    }
    
    _response_json = sa.call_api(endpoint='audio_features', params=params)

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
