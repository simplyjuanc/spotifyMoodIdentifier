import base64
import json
import os
from datetime import datetime, timedelta

import requests
from flask import Blueprint, request, session
from werkzeug.utils import redirect


auth_blueprint = Blueprint('auth_bp', __name__)


BASE_AUTH_URL = 'https://accounts.spotify.com/'    
CLIENT_URL = 'http://127.0.0.1:5000'
REDIRECT_URL = CLIENT_URL + '/callback'
BASE_URL = 'https://api.spotify.com/v1'

CLIENT_ID = os.environ.get('CLIENT_ID', None)
CLIENT_SECRET = os.environ.get('SECRET_KEY', None)
SCOPES = ['user-read-recently-played','playlist-modify-private']

ACCESS_TOKEN = None
REFRESH_TOKEN = None
TOKEN_TIMESTAMP = None
EXPIRES_IN = None



@auth_blueprint.route('/authorize')
def requestAuth():
    """
    Function that asks for initial user auth and then redirects to whitelisted URL.
    """
    AUTH_URL = BASE_AUTH_URL + 'authorize'
    params = {
        'client_id':CLIENT_ID,
        'response_type':'code',
        'redirect_uri':REDIRECT_URL,
        'scope': ' '.join(SCOPES)
    }

    requests.get(AUTH_URL, params=params, allow_redirects=True)
    return redirect('/callback')


@auth_blueprint.route('/callback')
def getAccessToken():
    TOKEN_URL =  BASE_AUTH_URL + 'api/token'
    
    data = {
        'grant_type':'authorization_code',
        'code':request.args['code'],
        'redirect_uri':REDIRECT_URL,
        'client_id':os.getenv('CLIENT_ID'),
        'client_secret':os.getenv('SECRET_KEY')
    } 

    token_response = requests.post(TOKEN_URL, data=data)
    token_json = json.loads(token_response.text)
    
    session['ACCESS_TOKEN'] = token_json['access_token']
    session['EXPIRES_IN'] = token_json['expires_in']
    session['REFRESH_TOKEN'] = token_json['refresh_token']
    session['TOKEN_TIMESTAMP'] = datetime.utcnow()
    session.modified = True

    return ACCESS_TOKEN


@auth_blueprint.route('/access')
def refreshToken():
    if session.get('ACCESS_TOKEN', None) == None:
        return requestAuth()
    else:
        requiresRefresh = session.get('TOKEN_TIMESTAMP', None) + timedelta(seconds=3600)
        if requiresRefresh < datetime.utcnow():
            return ACCESS_TOKEN
        else:
            _encodedSecrets = f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('ascii')
            encodedSecrets_bytes = base64.b64encode(_encodedSecrets)
            header = {
                'Authorization': 'Basic ' + encodedSecrets_bytes
            }
            params = {
                'grant_type': 'refresh_token',
                'refresh_token': session.get('REFRESH_TOKEN', None)
            }

            token_response = requests.post(BASE_AUTH_URL + 'api/token', params=params, headers=header)
            token_json = json.loads(token_response.text)
            
            session['ACCESS_TOKEN'] = token_json['access_token']
            session['EXPIRES_IN'] = token_json['expires_in']
            session['REFRESH_TOKEN'] = token_json['refresh_token']
            session['TOKEN_TIMESTAMP'] = datetime.utcnow()
            session.modified = True

            return ACCESS_TOKEN


def call_api(endpoint, params=None, payload=None):
    """
    Calls Spotify API with ACCESS_TOKEN, return JSON object for analysis.
    """
    call_url = BASE_URL + endpoint
    
    header = {
        'Authorization': 'Bearer {}'.format(refreshToken()),
        'Accept':'application/json',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(call_url, headers=header, data=payload, params=params)
    return json.loads(response.text)