import os
import requests, json
from flask import Flask, request, session, url_for
from werkzeug.utils import redirect
from flask_session import Session


BASE_AUTH_URL = 'https://accounts.spotify.com/'
REDIRECT_URL = 'http://127.0.0.1:5000/callback'

CLIENT_ID = os.environ.get('CLIENT_ID', None)
SECRET_KEY = os.environ.get('SECRET_KEY', None)
SCOPES = ['user-read-recently-played','playlist-modify-private']
ACCESS_TOKEN = None
REFRESH_TOKEN = None
EXPIRES_IN = None

auth = Flask(__name__)
auth.secret_key = os.urandom(64).hex()
auth.config['SESSION_TYPE'] = 'filesystem'
auth.config['SESSION_COOKIE_NAME'] = 'tests'
Session(auth)

@auth.route('/authorize')
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


@auth.route('/callback')
def getAccessToken():
    TOKEN_URL =  BASE_AUTH_URL + 'api/token'
    print('2:', request.url)
    print('2:', request.args)

    data = {
        'grant_type':'authorization_code',
        'code':request.args['code'],
        'redirect_uri':REDIRECT_URL,
        'client_id':os.getenv('CLIENT_ID'),
        'client_secret':os.getenv('SECRET_KEY')
    } 

    token_response = requests.post(TOKEN_URL, data=data)
    token_json = json.loads(token_response.text)
    
    session['access_token'] = token_json['access_token']
    session['expires_in'] = token_json['expires_in']
    session['refresh_token'] = token_json['refresh_token']
    session.modified = True

    return str(token_json)